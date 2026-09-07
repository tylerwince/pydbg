import importlib.util
import io
import json
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_pypi_release.py"
SPEC = importlib.util.spec_from_file_location("_check_pypi_release_tests", SCRIPT)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


def response(payload, status=200):
    result = io.BytesIO(json.dumps(payload).encode("utf-8"))
    result.status = status
    return result


def published_release(version):
    return {
        "info": {"name": "pydbg", "version": version},
        "urls": [{"packagetype": "sdist"}, {"packagetype": "bdist_wheel"}],
    }


def fail_with(error):
    def opener(request, *, timeout):
        raise error
    return opener


def test_missing_version_is_publishable_and_request_is_bounded():
    def opener(request, *, timeout):
        assert request.full_url == "https://pypi.org/pypi/pydbg/0.4.0%2Bbuild/json"
        assert timeout == 20
        assert request.get_header("Accept") == "application/json"
        raise HTTPError(request.full_url, 404, "Not Found", {}, None)

    assert release.should_publish("0.4.0+build", opener=opener) is True


def test_existing_matching_version_is_skipped():
    assert release.should_publish(
        "0.4.0",
        opener=lambda *args, **kwargs: response(published_release("0.4.0")),
    ) is False


@pytest.mark.parametrize("artifacts", [
    None,
    {},
    [],
    [{"packagetype": "sdist"}],
    [{"packagetype": "bdist_wheel"}],
    [None],
    [{}],
    [{"packagetype": []}],
    [{"packagetype": "sdist"}, {"packagetype": "bdist_wheel"}, {}],
])
def test_partial_or_malformed_release_requires_manual_recovery(artifacts):
    payload = published_release("0.4.0")
    payload["urls"] = artifacts
    with pytest.raises(ValueError, match="manual recovery"):
        release.should_publish(
            "0.4.0", opener=lambda *args, **kwargs: response(payload)
        )


@pytest.mark.parametrize("error", [
    HTTPError("https://pypi.org/", 403, "Forbidden", {}, None),
    HTTPError("https://pypi.org/", 429, "Too Many Requests", {}, None),
    HTTPError("https://pypi.org/", 500, "Server Error", {}, None),
    URLError("Connection failed"),
    TimeoutError("Request timed out"),
])
def test_network_failures_do_not_allow_publishing(error):
    with pytest.raises(type(error)):
        release.should_publish("0.4.0", opener=fail_with(error))


@pytest.mark.parametrize("payload", [
    [],
    {},
    {"info": None},
    {"info": {"name": "another-package", "version": "0.4.0"}},
    {"info": {"name": "pydbg", "version": "0.4.1"}},
])
def test_unexpected_package_data_fails_closed(payload):
    with pytest.raises(ValueError):
        release.should_publish(
            "0.4.0", opener=lambda *args, **kwargs: response(payload)
        )


def test_malformed_json_fails_closed():
    broken = io.BytesIO(b"not json")
    broken.status = 200
    with pytest.raises(ValueError):
        release.should_publish("0.4.0", opener=lambda *args, **kwargs: broken)


def test_unexpected_success_status_fails_closed():
    with pytest.raises(ValueError, match="status: 201"):
        release.should_publish(
            "0.4.0", opener=lambda *args, **kwargs: response({}, status=201)
        )


@pytest.mark.parametrize("publish", [True, False])
def test_cli_appends_github_outputs(publish, tmp_path, monkeypatch, capsys):
    output = tmp_path / "github-output"
    output.write_text("existing=true\n", encoding="utf-8")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    version = release.read_version()
    if publish:
        opener = fail_with(HTTPError("https://pypi.org/", 404, "Not Found", {}, None))
    else:
        opener = lambda *args, **kwargs: response(published_release(version))

    assert release.main([], opener=opener) == 0
    assert output.read_text(encoding="utf-8") == (
        f"existing=true\nshould-publish={str(publish).lower()}\nversion={version}\n"
    )
    captured = capsys.readouterr()
    assert version in captured.out
    assert ("publishing is allowed" if publish else "skipping upload") in captured.out
    assert captured.err == ""


def test_cli_error_returns_nonzero_without_outputs(tmp_path, monkeypatch, capsys):
    output = tmp_path / "github-output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    assert release.main([], opener=fail_with(URLError("Connection failed"))) == 1
    assert not output.exists()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Cannot determine whether to publish" in captured.err


def test_cli_partial_release_fails_without_outputs(tmp_path, monkeypatch, capsys):
    output = tmp_path / "github-output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    payload = published_release(release.read_version())
    payload["urls"] = [{"packagetype": "sdist"}]

    assert release.main([], opener=lambda *args, **kwargs: response(payload)) == 1
    assert not output.exists()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "partial release" in captured.err
    assert "manual recovery" in captured.err


def test_invalid_version_cannot_inject_github_outputs(tmp_path, monkeypatch):
    output = tmp_path / "github-output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setattr(release, "read_version", lambda: "0.4.0\nshould-publish=true")

    assert release.main([], opener=fail_with(AssertionError("Must not request"))) == 1
    assert not output.exists()

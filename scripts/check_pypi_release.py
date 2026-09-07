"""Decide whether this package version can be published without overwriting PyPI."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


# Load the sibling helper by path so isolated Python needs no checkout imports.
_spec = importlib.util.spec_from_file_location(
    "_pydbg_release_tag", Path(__file__).with_name("check_release_tag.py")
)
_release_tag = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_release_tag)
read_version = _release_tag.read_version


def should_publish(version: str, *, opener=urlopen) -> bool:
    """Return true only when PyPI explicitly reports this version is absent."""

    if not version or "\n" in version or "\r" in version:
        raise ValueError("Package version must be a nonempty single-line string")

    request = Request(
        f"https://pypi.org/pypi/pydbg/{quote(version, safe='')}/json",
        headers={"Accept": "application/json", "User-Agent": "pydbg-release-check"},
    )
    try:
        with opener(request, timeout=20) as response:
            if response.status != 200:
                raise ValueError(f"Unexpected PyPI response status: {response.status}")
            payload = json.load(response)
    except HTTPError as error:
        if error.code == 404:
            return True
        raise

    info = payload.get("info") if isinstance(payload, dict) else None
    if not isinstance(info, dict):
        raise ValueError("PyPI response is missing package information")
    if info.get("name") != "pydbg" or info.get("version") != version:
        raise ValueError("PyPI response does not match the requested project and version")

    artifacts = payload.get("urls")
    if not isinstance(artifacts, list) or any(
        not isinstance(artifact, dict)
        or not isinstance(artifact.get("packagetype"), str)
        for artifact in artifacts
    ):
        raise ValueError(
            "PyPI release artifact metadata is malformed; manual recovery required"
        )
    package_types = {artifact["packagetype"] for artifact in artifacts}
    if not {"sdist", "bdist_wheel"}.issubset(package_types):
        raise ValueError(
            "PyPI contains a partial release without both sdist and wheel; "
            "manual recovery required"
        )
    return False


def main(arguments: list[str] | None = None, *, opener=urlopen) -> int:
    arguments = sys.argv[1:] if arguments is None else arguments
    if arguments:
        print("usage: check_pypi_release.py", file=sys.stderr)
        return 2

    try:
        version = read_version()
        publish = should_publish(version, opener=opener)
        output_path = os.environ.get("GITHUB_OUTPUT")
        if output_path:
            with Path(output_path).open("a", encoding="utf-8") as output:
                output.write(f"should-publish={str(publish).lower()}\nversion={version}\n")
    except (OSError, ValueError, RuntimeError, SyntaxError) as error:
        print(f"Cannot determine whether to publish pydbg: {error}", file=sys.stderr)
        return 1

    if publish:
        print(f"pydbg {version} is absent from PyPI; publishing is allowed.")
    else:
        print(f"pydbg {version} is already published on PyPI; skipping upload.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

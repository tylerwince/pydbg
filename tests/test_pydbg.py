import inspect
import io
import logging
import subprocess
import sys
from pathlib import Path
from threading import Thread

import pydbg as pydbg_module
from pydbg import dbg, format_dbg


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_TAG_CHECK = PROJECT_ROOT / "scripts" / "check_release_tag.py"
CURRENT_RELEASE_TAG = f"v{pydbg_module.__version__}"


def _debug_value(value):
    return dbg(value)


def test_dbg_prints_expression_and_returns_value(capsys):
    value = {"answer": 42}

    result = dbg(value)

    assert result is value
    assert capsys.readouterr().err.endswith("] value = {'answer': 42}\n")


def test_dbg_uses_the_immediate_calling_frame(capsys):
    expected_line = inspect.getsourcelines(_debug_value)[1] + 1

    assert _debug_value(3) == 3

    assert capsys.readouterr().err == (
        f"[{__file__}:{expected_line}] value = 3\n"
    )


def test_nested_function_argument_uses_only_dbg_argument(capsys):
    result = int(1 + dbg(1))

    assert result == 2
    assert capsys.readouterr().err.endswith("] 1 = 1\n")


def test_multiline_expression_is_recovered(capsys):
    result = dbg(
        sum(
            [1, 2, 3]
        )
    )

    assert result == 6
    assert capsys.readouterr().err.endswith(
        "] sum(\n"
        "            [1, 2, 3]\n"
        "        ) = 6\n"
    )


def test_repeated_calls_on_one_line_are_disambiguated(capsys):
    left, right = "left", "right"

    dbg(left), dbg(right)

    messages = capsys.readouterr().err.splitlines()
    assert messages[0].endswith("] left = 'left'")
    assert messages[1].endswith("] right = 'right'")


def test_alias_call_is_still_resolved(capsys):
    inspect_value = dbg
    value = 4

    result = inspect_value(value)

    assert result == 4
    assert capsys.readouterr().err.endswith("] value = 4\n")


def test_module_qualified_call_is_still_resolved(capsys):
    value = 5

    result = pydbg_module.dbg(value)

    assert result == 5
    assert capsys.readouterr().err.endswith("] value = 5\n")


def test_sorted_callback_falls_back_instead_of_mislabeling(capsys):
    result = sorted([3, 1], key=dbg)

    assert result == [1, 3]
    messages = capsys.readouterr().err.splitlines()
    assert messages[0].endswith("] <expression unavailable> = 3")
    assert messages[1].endswith("] <expression unavailable> = 1")


def test_map_callback_falls_back_instead_of_mislabeling(capsys):
    result = list(map(dbg, [10, 20]))

    assert result == [10, 20]
    messages = capsys.readouterr().err.splitlines()
    assert messages[0].endswith("] <expression unavailable> = 10")
    assert messages[1].endswith("] <expression unavailable> = 20")


def test_starred_argument_falls_back_instead_of_mislabeling(capsys):
    payload = (7,)

    result = dbg(*payload)

    assert result == 7
    assert capsys.readouterr().err.endswith(
        "] <expression unavailable> = 7\n"
    )


def test_thread_callback_falls_back_instead_of_mislabeling(capsys):
    thread = Thread(target=dbg, args=(42,))

    thread.start()
    thread.join()

    assert not thread.is_alive()
    assert capsys.readouterr().err.endswith(
        "] <expression unavailable> = 42\n"
    )


def test_expression_in_function_is_recovered(capsys):
    def increment(value):
        return dbg(value + 1)

    assert increment(4) == 5
    assert capsys.readouterr().err.endswith("] value + 1 = 5\n")


def test_expression_in_comprehension_is_recovered(capsys):
    assert [dbg(value * 2) for value in range(2)] == [0, 2]

    messages = capsys.readouterr().err.splitlines()
    assert messages[0].endswith("] value * 2 = 0")
    assert messages[1].endswith("] value * 2 = 2")


def test_expression_in_lambda_is_recovered(capsys):
    inspect_value = lambda value: dbg(value + 1)

    assert inspect_value(4) == 5
    assert capsys.readouterr().err.endswith("] value + 1 = 5\n")


def test_keyword_argument_is_recovered(capsys):
    result = dbg(exp=7)

    assert result == 7
    assert capsys.readouterr().err.endswith("] 7 = 7\n")


def test_format_dbg_integrates_with_logging(capsys):
    output = io.StringIO()
    logger = logging.Logger("pydbg-test", level=logging.DEBUG)
    logger.addHandler(logging.StreamHandler(output))
    value = 9

    logger.debug("%s", format_dbg(value))

    assert capsys.readouterr().err == ""
    assert output.getvalue().endswith("] value = 9\n")


def test_source_unavailable_falls_back_without_crashing(capsys):
    namespace = {"dbg": dbg}

    exec(compile("dbg(42)", "<repl>", "exec"), namespace)

    assert capsys.readouterr().err == (
        "[<repl>:1] <expression unavailable> = 42\n"
    )


def test_python_c_falls_back_without_crashing(tmp_path, monkeypatch):
    # A checkout or PYTHONPATH entry must not hide a broken installed wheel.
    (tmp_path / "pydbg.py").write_text(
        "raise RuntimeError('Imported the checkout instead of the wheel')\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))

    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            "from pydbg import dbg; assert dbg(1) == 1",
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == (
        "[<string>:1] <expression unavailable> = 1\n"
    )


def test_release_tag_check_accepts_matching_version():
    result = subprocess.run(
        [sys.executable, RELEASE_TAG_CHECK, CURRENT_RELEASE_TAG],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert "matches the package version" in result.stdout


def test_release_tag_check_rejects_mismatched_version():
    result = subprocess.run(
        [sys.executable, RELEASE_TAG_CHECK, "v999.0.0"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert f"expected {CURRENT_RELEASE_TAG!r}" in result.stderr

"""Fail a release when its Git tag does not match pydbg's package version."""

from __future__ import annotations

import ast
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "pydbg.py"


def read_version(module_path: Path = MODULE_PATH) -> str:
    tree = ast.parse(module_path.read_text(encoding="utf-8"), module_path.name)

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "__version__"
            for target in node.targets
        ):
            continue

        version = ast.literal_eval(node.value)
        if isinstance(version, str):
            return version

    raise RuntimeError(f"Could not find a string __version__ in {module_path}")


def main(arguments: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if arguments is None else arguments
    if len(arguments) != 1:
        print("usage: check_release_tag.py RELEASE_TAG", file=sys.stderr)
        return 2

    release_tag = arguments[0]
    expected_tag = f"v{read_version()}"
    if release_tag != expected_tag:
        print(
            f"Release tag {release_tag!r} does not match "
            f"package version; expected {expected_tag!r}.",
            file=sys.stderr,
        )
        return 1

    print(f"Release tag {release_tag!r} matches the package version.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

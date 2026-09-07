# Releasing pydbg

Merge a reviewed version bump into `master` to release it. There is no separate
GitHub release or tag required to start publishing.

The release workflow uses the same build-and-test workflow as CI. It builds a
source distribution and a universal wheel once, checks both artifacts, and
tests the installed wheel on Python 3.10 through 3.14. The wheel is built from
the source distribution, so a missing source file cannot be hidden by the
checkout. Tests use isolated Python imports, including subprocesses.

Publishing waits for every supported Python version to pass. If the package
version is not already on PyPI, it uploads those same artifacts without
rebuilding them. An existing version with both source and wheel artifacts is
skipped, so ordinary merges do not attempt duplicate releases. A failed build,
test, or PyPI availability check
prevents publishing. No long-lived PyPI token is stored in GitHub.

Publishing runs are serialized so two merges cannot publish the same version
concurrently. After correcting a failed setup or transient service problem,
use **Run workflow** on **Publish to PyPI**, selecting `master`, to retry. Manual
runs from other branches cannot publish.

If an upload only partially succeeded, the next run fails rather than silently
skipping it or mixing artifacts from different commits. Recover the missing
file from that original run's `python-package-distributions` artifact, or
release a new version; do not rebuild a missing file under the old version.

## One-time trusted publishing setup

1. In the PyPI settings for `pydbg`, add a GitHub trusted publisher.
2. Use `tylerwince` as the owner, `pydbg` as the repository,
   `publish.yml` as the workflow, and `pypi` as the environment.
3. Create a GitHub environment named `pypi` and restrict deployments to the
   `master` branch. Do not restrict it to tags: this workflow runs on a merge.
4. Treat PR review and merge as the release approval. A required environment
   reviewer is optional, but enabling one adds a separate approval after merge.
5. Confirm the publisher and environment settings before merging the first
   release PR. Without them, publishing may fail even though package tests pass.

## Release checklist

1. Update `__version__` in `pydbg.py` to an unpublished version and prepare
   release notes. Version 0.4.0 requires Python 3.10 or newer; call out that
   compatibility change.
2. Run the local checks below and review the changes. Commit and push only with
   the maintainer's approval.
3. Open a PR and wait for CI to pass on every supported Python version.
4. Review and merge the PR into `master`. This starts the publishing workflow,
   which rebuilds and tests the exact merge commit before publishing.
5. Verify the new version, source distribution, and wheel on PyPI. In a fresh
   environment, install `pydbg==0.4.0` from PyPI and run
   `python -I -c 'from pydbg import dbg; assert dbg(42) == 42'`. Expect the
   explicit `<expression unavailable>` fallback for this command-line check.

## Local checks

From a development environment installed with `python -m pip install -e ".[dev]"`:

```console
python -m pytest
python -m build
python -m twine check dist/*
```

To reproduce CI's installed-wheel checks, create a fresh virtual environment
with a supported Python version, then run from the repository root:

```console
python -m pip install "dist/pydbg-0.4.0-py3-none-any.whl[test]"
python -I -m pytest --import-mode=importlib
```

Do not install the checkout in editable mode in that environment. Repeat with
each supported Python version; CI enforces the full matrix before publishing.

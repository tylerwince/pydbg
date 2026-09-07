# Changelog

## 0.4.0

### Compatibility

- Requires Python 3.10 or newer. Tested on CPython 3.10 through 3.14.
- Adds `executing>=2.2.1` as a runtime dependency for precise source inspection.

### Added

- `format_dbg(value)` returns the debug message without printing it, for use
  with logging and other output destinations.
- Source distributions and universal wheels built with `pyproject.toml`.
- GitHub Actions tests the installed wheel on every supported Python version
  before the same artifacts can be published through PyPI Trusted Publishing.
  Merging an unpublished version into `master` starts the release; already
  published versions are skipped.

### Fixed

- Reports the immediate caller's source location.
- Recovers the inspected argument in nested and multiline expressions,
  repeated calls on one line, functions, comprehensions, and lambdas.
- Resolves direct aliases, module-qualified calls, and the `exp` keyword.
- Falls back to `<expression unavailable>` when source or the exact argument
  cannot be recovered, including callbacks and argument unpacking, instead of
  reporting an unrelated expression.

`dbg(value)` continues to write to standard error and return the original value.

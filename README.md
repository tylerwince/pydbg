# pydbg 🐛

[![CI](https://github.com/tylerwince/pydbg/actions/workflows/ci.yml/badge.svg)](https://github.com/tylerwince/pydbg/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pydbg.svg)](https://pypi.org/project/pydbg/)
[![Python](https://img.shields.io/pypi/pyversions/pydbg.svg)](https://pypi.org/project/pydbg/)

`pydbg` is an expression-aware implementation of
[Rust's `dbg!` macro](https://doc.rust-lang.org/std/macro.dbg.html) for Python.
It is a small tool for people who debug with print statements.

```console
python -m pip install pydbg
```

Python 3.10 through 3.14 are supported.

## Usage

```python
from pydbg import dbg

a = 2
b = 3

result = dbg(a + b)

assert result == 5
```

`dbg` writes the source location, expression, and value to standard error:

```text
[example.py:6] a + b = 5
```

The original value is returned, so `dbg` can be inserted inside a larger
expression:

```python
total = int(1 + dbg(2))
```

```text
[example.py:1] 2 = 2
```

Nested, multiline, repeated, comprehension, lambda, and function calls are
resolved against the exact executing AST node. When source is unavailable, as
in some REPL and `python -c` sessions, or the call cannot be matched reliably,
as with callbacks and argument unpacking, `pydbg` still reports the location
and value with an explicit fallback:

```text
[<string>:1] <expression unavailable> = 2
```

## Logging integration

Use `format_dbg` when another system should handle the output:

```python
import logging

from pydbg import format_dbg

logging.basicConfig(level=logging.DEBUG)
value = 42
logging.debug("%s", format_dbg(value))
```

It returns the same formatted message without writing to standard error.

## Development

```console
python -m pip install --editable ".[dev]"
python -m pytest
python -m build
python -m twine check dist/*
```

See [RELEASING.md](RELEASING.md) for the Trusted Publishing release flow.
See [CHANGELOG.md](CHANGELOG.md) for release notes and compatibility changes.

## Contributors

Thanks to everyone who has submitted an issue or thoughts on this project.
Special thanks to those who have submitted a PR to make this project better
for everyone:

- [besfahbod](https://github.com/besfahbod)
- [tqhdesilva](https://github.com/tqhdesilva)

## License

MIT. See [LICENSE](LICENSE).

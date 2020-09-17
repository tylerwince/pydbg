# pydbg 🐛 [![Build Status](https://travis-ci.org/tylerwince/pydbg.svg?branch=master)](https://travis-ci.org/tylerwince/pydbg)

`pydbg` is an implementation of the [Rust builtin debugging macro `dbg`](https://rust-lang.github.io/rfcs/2361-dbg-macro.html)

The purpose of this package is to provide a better and more effective workflow for
people who are "print debuggers".

`pip install pydbg`

## The old way:

```python

a = 2
b = 3

print(f"a + b after instatiated = {a+b}")

def square(x: int) -> int:
    return x * x

print(f"a squared with my function = {square(a)}")

```
outputs:

```
a + b after instatiated = 5
a squared with my function = 4
```

## The _new_ (and better) way

```python
from pydbg import dbg

a = 2
b = 3

dbg(a+b)

def square(x: int) -> int:
    return x * x

dbg(square(a))

```
outputs:

```
[testfile.py:4] a+b = 5
[testfile.py:9] square(a) = 4
```

### This project is a work in progress and all feedback is appreciated.

The next features that are planned are:

- [ ] Fancy Mode (display information about the whole callstack)
- [ ] Performance Optimizations
- [ ] Typing information

## CONTRIBUTORS:

Thanks to everyone who has submitted an issue or thoughts on this project.
Special thanks to those who have submitted a PR to make this project better for everyone:

- [besfahbod](https://github.com/besfahbod)
- [tqhesilva](https://github.com/tqhdesilva)


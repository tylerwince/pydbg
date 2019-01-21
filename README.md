# pydbg 🐛 [![Build Status](https://travis-ci.com/tylerwince/pydbg.svg?branch=master)](https://travis-ci.com/tylerwince/pydbg)

`pydbg` is an implementation of the Rust2018 builtin debugging macro `dbg`.

The purpose of this package is to provide a better and more effective workflow for
people who are "print debuggers".

`pip install pydbg`

`from pydbg import dbg`

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

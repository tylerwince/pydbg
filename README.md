# pydbg
---

`pydbg` is an implementation of the Rust2018 builtin debugging helper function `dbg`.

The purpose of this package is to provide a better and more effective workflow for
people who are "print debuggers". Using this package changes your workflow from:

```python

a = 2
b = 3

print(f"a + b after instatiated = {a+b}")

def square(x: int) -> int:
    return x * x

print(f"a squared with my function = {square(a)}")

```
which outputs:

```
a + b after instatiated = 5
a squared with my functioin = 4
```

to a much simpler and more informative workflow:

```python

a = 2
b = 3

dbg(a+b)

def square(x: int) -> int:
    return x * x

dbg(square(a))

```

which outputs:

```
[testfile.py:4] a+b = 5
[testfile.py:9] square(a) = 4
```

### This project is a work in progress and all feedback is appreciated.

The next features that are planned are:

[ ] Fancy Mode (display information about the whole callstack)
[ ] Performance Optimizations
[ ] Typing information

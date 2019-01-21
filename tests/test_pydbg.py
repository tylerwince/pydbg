import io
from pydbg import dbg
from contextlib import redirect_stdout


def something():
    pass


def test_variables():
    intType = 2
    floatType = 2.1
    strType = "mystring"
    boolType = True
    NoneType = None

    out = io.StringIO()
    with redirect_stdout(out):
        dbg(intType)
        dbg(floatType)
        dbg(strType)
        dbg(boolType)
        dbg(NoneType)

    print(out.getvalue())

    want = """[/Users/tyler/go/src/github.com/tylerwince/pydbg/test_pydbg.py:19] intType = 2
[/Users/tyler/go/src/github.com/tylerwince/pydbg/test_pydbg.py:20] floatType = 2.1
[/Users/tyler/go/src/github.com/tylerwince/pydbg/test_pydbg.py:21] strType = mystring
[/Users/tyler/go/src/github.com/tylerwince/pydbg/test_pydbg.py:22] boolType = True
[/Users/tyler/go/src/github.com/tylerwince/pydbg/test_pydbg.py:23] NoneType = None
"""

    assert out.getvalue() == want

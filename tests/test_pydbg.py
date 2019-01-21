import os
import io
from pydbg import dbg
from contextlib import redirect_stdout


cwd = os.getcwd()

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
        dbg(add(1, 2))

    want = f"""[{cwd}/tests/test_pydbg.py:18] intType = 2
[{cwd}/tests/test_pydbg.py:19] floatType = 2.1
[{cwd}/tests/test_pydbg.py:20] strType = mystring
[{cwd}/tests/test_pydbg.py:21] boolType = True
[{cwd}/tests/test_pydbg.py:22] NoneType = None
[{cwd}/tests/test_pydbg.py:23] add(1, 2) = 3
"""

    assert out.getvalue()  == want


def add(x, y):
    return x + y


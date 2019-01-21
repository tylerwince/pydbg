import os
import io
from pydbg import dbg
from contextlib import redirect_stdout


def something():
    pass

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

    want = f"""[{cwd}/tests/test_pydbg.py:21] intType = 2
[{cwd}/tests/test_pydbg.py:22] floatType = 2.1
[{cwd}/tests/test_pydbg.py:23] strType = mystring
[{cwd}/tests/test_pydbg.py:24] boolType = True
[{cwd}/tests/test_pydbg.py:25] NoneType = None
"""

    assert out.getvalue() == want

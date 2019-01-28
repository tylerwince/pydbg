import os
import io
from pydbg import dbg
from contextlib import redirect_stdout


cwd = os.getcwd()

def test_variables():
    NoneType = None
    boolType = True
    intType = 2
    floatType = 3.4
    strType = "mystring"
    strType1 = "None"
    strType2 = "True"
    strType3 = "2"
    strType4 = "3.4"

    out = io.StringIO()
    with redirect_stdout(out):
        dbg(NoneType)
        dbg(boolType)
        dbg(intType)
        dbg(floatType)
        dbg(strType)
        dbg(strType1)
        dbg(strType2)
        dbg(strType3)
        dbg(strType4)
        dbg(add(5, 6))

    want = f"""\
[{cwd}/tests/test_pydbg.py:22] NoneType = None
[{cwd}/tests/test_pydbg.py:23] boolType = True
[{cwd}/tests/test_pydbg.py:24] intType = 2
[{cwd}/tests/test_pydbg.py:25] floatType = 3.4
[{cwd}/tests/test_pydbg.py:26] strType = 'mystring'
[{cwd}/tests/test_pydbg.py:27] strType1 = 'None'
[{cwd}/tests/test_pydbg.py:28] strType2 = 'True'
[{cwd}/tests/test_pydbg.py:29] strType3 = '2'
[{cwd}/tests/test_pydbg.py:30] strType4 = '3.4'
[{cwd}/tests/test_pydbg.py:31] add(5, 6) = 11
"""

    assert out.getvalue()  == want


def add(x, y):
    return x + y


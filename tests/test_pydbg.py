import io
import os
from contextlib import redirect_stderr

from pydbg import dbg


CWD = os.getcwd()


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
    with redirect_stderr(out):
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
    assert out.getvalue() == f"""\
[{CWD}/tests/test_pydbg.py:24] NoneType = None
[{CWD}/tests/test_pydbg.py:25] boolType = True
[{CWD}/tests/test_pydbg.py:26] intType = 2
[{CWD}/tests/test_pydbg.py:27] floatType = 3.4
[{CWD}/tests/test_pydbg.py:28] strType = 'mystring'
[{CWD}/tests/test_pydbg.py:29] strType1 = 'None'
[{CWD}/tests/test_pydbg.py:30] strType2 = 'True'
[{CWD}/tests/test_pydbg.py:31] strType3 = '2'
[{CWD}/tests/test_pydbg.py:32] strType4 = '3.4'
[{CWD}/tests/test_pydbg.py:33] add(5, 6) = 11
"""


def add(x, y):
    return x + y

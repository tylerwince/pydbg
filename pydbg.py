"""pydbg is an implementation of the Rust2018 builtin `dbg` for Python."""
import inspect

__version__ = "0.1.0"


def dbg(exp):
    """Call dbg with any variable or expression.

    Calling debug will print out the content information (file, lineno) as wil as the
    passed expression and what the expression is equal to::

        from pydbg import dbg

        a = 2
        b = 5

        dbg(a+b)

        def square(x: int) -> int:
            return x * x

        dbg(square(a))

    """

    for i in reversed(inspect.stack()):
        if "dbg" in i.code_context[0]:
            var_name = i.code_context[0][
                i.code_context[0].find("(")
                + 1 : len(i.code_context[0])
                - 1
                - i.code_context[0][::-1].find(")")
            ]
            print(f"[{i.filename}:{i.lineno}] {var_name} = {exp}")
            break

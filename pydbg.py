"""pydbg is an implementation of the Rust2018 builtin `dbg` for Python."""
import inspect

__version__ = "0.2.1"


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
        ctx = i.code_context[0]
        if "dbg" in ctx:
            print(
                f"[{i.filename}:{i.lineno}] {ctx[ctx.find('(') + 1 : ctx.rfind(')')]} = {exp!r}"
            )
            break
    return exp

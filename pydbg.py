"""A small, expression-aware debugging print helper."""

from __future__ import annotations

import ast
import inspect
import sys
from types import FrameType
from typing import TypeVar

from executing import Source


__all__ = ["dbg", "format_dbg"]
__version__ = "0.4.0"


_ExpType = TypeVar("_ExpType")
_EXPRESSION_UNAVAILABLE = "<expression unavailable>"
_UNRESOLVED = object()


def _caller_frame() -> FrameType | None:
    """Return the frame that called the public pydbg function."""

    current_frame = inspect.currentframe()
    try:
        if current_frame is None or current_frame.f_back is None:
            return None
        return current_frame.f_back.f_back
    finally:
        del current_frame


def _resolve_reference(frame: FrameType, node: ast.expr) -> object:
    """Resolve a simple source reference without executing user code."""

    if isinstance(node, ast.Name):
        for namespace in (frame.f_locals, frame.f_globals, frame.f_builtins):
            if node.id in namespace:
                return namespace[node.id]
        return _UNRESOLVED

    if isinstance(node, ast.Attribute):
        owner = _resolve_reference(frame, node.value)
        if owner is _UNRESOLVED:
            return _UNRESOLVED
        return inspect.getattr_static(owner, node.attr, _UNRESOLVED)

    return _UNRESOLVED


def _expression_source(frame: FrameType, expected_callable: object) -> str:
    """Return the exact source for the argument being inspected, when available."""

    try:
        execution = Source.executing(frame)
        node = execution.node
        if not isinstance(node, ast.Call):
            return _EXPRESSION_UNAVAILABLE
        if _resolve_reference(frame, node.func) is not expected_callable:
            return _EXPRESSION_UNAVAILABLE

        if node.args:
            argument = node.args[0]
            if isinstance(argument, ast.Starred):
                return _EXPRESSION_UNAVAILABLE
        else:
            argument = next(
                (
                    keyword.value
                    for keyword in node.keywords
                    if keyword.arg == "exp"
                ),
                None,
            )

        if argument is None:
            return _EXPRESSION_UNAVAILABLE

        expression = ast.get_source_segment(execution.source.text, argument)
        return expression or _EXPRESSION_UNAVAILABLE
    except Exception:
        # Debug output must not break the program when source inspection fails.
        return _EXPRESSION_UNAVAILABLE


def _format(
    exp: object,
    frame: FrameType | None,
    expected_callable: object,
) -> str:
    if frame is None:
        filename = "<unknown>"
        lineno = 0
        expression = _EXPRESSION_UNAVAILABLE
    else:
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        expression = _expression_source(frame, expected_callable)

    return f"[{filename}:{lineno}] {expression} = {exp!r}"


def format_dbg(exp: object) -> str:
    """Format debug context for an expression without writing any output.

    This is useful with logging frameworks and other output destinations:

        logger.debug("%s", format_dbg(value))
    """

    return _format(exp, _caller_frame(), format_dbg)


def dbg(exp: _ExpType) -> _ExpType:
    """Print an expression and its value to stderr, then return the value."""

    print(_format(exp, _caller_frame(), dbg), file=sys.stderr)
    return exp

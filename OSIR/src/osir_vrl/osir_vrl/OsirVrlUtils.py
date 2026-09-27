from __future__ import annotations
import re
from typing import Any, Optional


def extract_vrl_fields(expr: str) -> list[str]:
    """Return deduplicated .field references from a VRL expression, ignoring string literals.

    Supports plain fields (.foo.bar), quoted segments (."#text"), and mixed chains
    (.Event.System.EventID."#text").
    """
    # One segment: either .<ident> or ."<any chars>"
    _SEG = r'(?:\.[a-zA-Z_@][a-zA-Z0-9_]*|\.\"[^\"]+\")'
    # A field path is one or more segments
    fields = re.findall(r'(' + _SEG + r'(?:' + _SEG + r')*)', expr)
    return list(dict.fromkeys(fields))


def render_value(val: Any) -> str:
    if isinstance(val, bool): return "true" if val else "false"
    if isinstance(val, str):  return f'"{val}"'
    if isinstance(val, list): return "[" + ", ".join(f'"{i}"' for i in val) + "]"
    return str(val)


def condition_guard(field: str, value: Any, exists: Optional[bool] = None) -> str:
    """VRL guard for one declarative condition: no value -> exists(),
    `exists: false` -> !exists(), otherwise an equality test (same semantics
    for transformation entries and timeline entries)."""
    path = f".{field}"
    if exists is False:
        return f"!exists({path})"
    if value is None:
        return f"exists({path})"
    if isinstance(value, bool):
        return f"{path} == {'true' if value else 'false'}"
    if isinstance(value, str):
        return f'{path} == "{value}"'
    return f"{path} == {value}"

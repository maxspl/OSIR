from __future__ import annotations
import re
from typing import Any


class VRL(str):
    pass


def parse_vrl_tag(value: Any) -> Any:
    if isinstance(value, str):
        if value.startswith('v"') and value.endswith('"'):
            return VRL(value[2:-1])
        if value.startswith("v'") and value.endswith("'"):
            return VRL(value[2:-1])
        if value.startswith("v|") or value.startswith("v>"):
            return VRL(value[2:].strip())
    if isinstance(value, dict):
        return {k: parse_vrl_tag(v) for k, v in value.items()}
    if isinstance(value, list):
        return [parse_vrl_tag(i) for i in value]
    return value


def extract_vrl_fields(expr: str) -> list[str]:
    """Return deduplicated .field references from a VRL expression, ignoring string literals."""
    cleaned = re.sub(r'"[^"]*"', '""', expr)
    fields  = re.findall(r'(\.[a-zA-Z_@][a-zA-Z0-9_.]*)', cleaned)
    return list(dict.fromkeys(fields))


def render_value(val: Any) -> str:
    if isinstance(val, VRL):  return str(val)
    if isinstance(val, bool): return "true" if val else "false"
    if isinstance(val, str):  return f'"{val}"'
    if isinstance(val, list): return "[" + ", ".join(f'"{i}"' for i in val) + "]"
    return str(val)

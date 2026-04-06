from __future__ import annotations
import re
from typing import Any, Optional
from pydantic import BaseModel


class Condition(BaseModel):
    field: str
    value: Optional[Any] = None


class Relationship(BaseModel):
    source: str
    target: str
    type:   str


class Description(BaseModel):
    message:       str
    conditions:    list[Condition]    = []
    relationships: list[Relationship] = []

    def to_vrl(self) -> str:
        guards   = self._build_guards()
        template = self._build_template()
        body: list[str] = [f".message = {template}"]
        for rel in self.relationships:
            body.append('if !is_array(.relationships) { .relationships = [] }')
            body.append(
                f'.relationships = push!(.relationships, {{'
                f'"source": to_string!(.{rel.source}), '
                f'"target": to_string!(.{rel.target}), '
                f'"type": "{rel.type}"}})'
            )
        if guards:
            inner = "\n  ".join(body)
            return f"if {guards} {{\n  {inner}\n}}"
        return "\n".join(body)

    def _template_fields(self) -> list[str]:
        return re.findall(r'\{([^}]+)\}', self.message)

    def _build_guards(self) -> str:
        parts = []
        condition_fields = {c.field for c in self.conditions}
        for c in self.conditions:
            field = f".{c.field}"
            if c.value is None:
                parts.append(f"exists({field})")
            elif isinstance(c.value, bool):
                parts.append(f"{field} == {'true' if c.value else 'false'}")
            elif isinstance(c.value, str):
                parts.append(f'{field} == "{c.value}"')
            else:
                parts.append(f"{field} == {c.value}")
        for f in self._template_fields():
            if f not in condition_fields:
                parts.append(f"exists(.{f})")
        return " && ".join(parts)

    def _build_template(self) -> str:
        parts   = []
        last    = 0
        pattern = re.compile(r'\{([^}]+)\}')
        for match in pattern.finditer(self.message):
            if match.start() > last:
                parts.append(f'"{self.message[last:match.start()]}"')
            parts.append(f"to_string!(.{match.group(1)})")
            last = match.end()
        if last < len(self.message):
            parts.append(f'"{self.message[last:]}"')
        return " + ".join(parts)

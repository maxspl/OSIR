from __future__ import annotations
import re
from typing import Any, Optional
from pydantic import BaseModel, model_validator
from .OsirVrlUtils import condition_guard


class OsirVrlCondition(BaseModel):
    """One declarative condition: no value -> exists(), `exists: false` ->
    !exists(), otherwise an equality test."""
    model_config = {"extra": "forbid"}
    field: str
    value: Optional[Any] = None
    exists: Optional[bool] = None

    @model_validator(mode="after")
    def _validate_shape(self) -> "OsirVrlCondition":
        if self.exists is not None and self.value is not None:
            raise ValueError("a condition takes either a value or exists, not both")
        return self


class OsirVrlRelationship(BaseModel):
    """A relationship attached to a timeline entry: `id` is the id of the
    timeline element the relationship belongs to."""
    model_config = {"extra": "forbid"}
    id:     str
    source: str
    target: str
    type:   str


class OsirVrlTimelineEntry(BaseModel):
    model_config = {"extra": "forbid"}
    id:            Optional[str]               = None
    message:       str
    conditions:    list[OsirVrlCondition]      = []

    def to_vrl(self, relationships: Optional[list[OsirVrlRelationship]] = None) -> str:
        rels = relationships or []
        guards   = self._build_guards()
        template = self._build_template()
        body: list[str] = [f".message = {template}"]
        for rel in rels:
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
            parts.append(condition_guard(c.field, c.value, c.exists))
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

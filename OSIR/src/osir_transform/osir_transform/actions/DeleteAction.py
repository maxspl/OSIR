from __future__ import annotations
from pydantic import BaseModel


class DeleteAction(BaseModel):
    delete: list[str]

    def to_vrl(self, flat_fields: set[str] = frozenset()) -> list[str]:
        lines = []
        for f in self.delete:
            if " " in f:
                lines.append(f'del(."{f}")')
            elif "." in f and f in flat_fields:
                lines.append(f'del(."{f}")')
            else:
                lines.append(f"del(.{f})")
        return lines

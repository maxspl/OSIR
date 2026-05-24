from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from ..VRL import VRL


class DeleteAction(BaseModel):
    delete: list[str]
    filter: Optional[VRL] = None
    model_config = {"arbitrary_types_allowed": True}

    def to_vrl(self, flat_fields: set[str] = frozenset()) -> list[str]:
        if self.filter:
            lines = [f"if {self.filter} {{"]
            for f in self.delete:
                if " " in f:
                    lines.append(f'  del(."{f}")')
                elif "." in f and f in flat_fields:
                    lines.append(f'  del(."{f}")')
                else:
                    lines.append(f"  del(.{f})")
            lines.append("}")
            return lines

        lines = []
        for f in self.delete:
            if " " in f:
                lines.append(f'del(."{f}")')
            elif "." in f and f in flat_fields:
                lines.append(f'del(."{f}")')
            else:
                lines.append(f"del(.{f})")
        return lines

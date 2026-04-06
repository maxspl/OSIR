from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel
from ..VRL import VRL, extract_vrl_fields, render_value


class SetAction(BaseModel):
    set:    dict[str, Any]
    filter: Optional[VRL] = None
    model_config = {"arbitrary_types_allowed": True}

    def to_vrl(self) -> list[str]:
        if self.filter:
            lines = [f"if {self.filter} {{"]
            for dst, val in self.set.items():
                lines.extend(self._stmt_lines(dst, val, indent="  "))
            lines.append("}")
            return lines

        lines = []
        for dst, val in self.set.items():
            lines.extend(self._stmt_lines(dst, val))
        return lines

    def _stmt_lines(self, dst: str, val: Any, indent: str = "") -> list[str]:
        stmt = f"{indent}.{dst} = {render_value(val)}"
        if not isinstance(val, VRL):
            return [stmt]
        fields = extract_vrl_fields(str(val))
        if not fields:
            return [stmt]
        guard = " && ".join(f"exists({f})" for f in fields)
        return [
            f"{indent}if {guard} {{",
            f"{indent}  .{dst} = {render_value(val)}",
            f"{indent}}}",
        ]

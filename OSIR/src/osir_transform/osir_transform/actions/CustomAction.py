from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel
from ..VRL import VRL


class CustomAction(BaseModel):
    custom:  dict[str, Any]
    filter:  Optional[VRL] = None
    model_config = {"arbitrary_types_allowed": True}

    def to_vrl(self) -> list[str]:
        if self.filter:
            lines = [f"if {self.filter} {{"]
            for vrl_code in self.custom.values():
                lines.append(f"  {vrl_code}")
            lines.append("}")
            return lines

        lines = []
        for vrl_code in self.custom.values():
            lines.append(str(vrl_code))
        return lines

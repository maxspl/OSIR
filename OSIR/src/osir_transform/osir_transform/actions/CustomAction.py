from __future__ import annotations
from typing import Any
from pydantic import BaseModel


class CustomAction(BaseModel):
    custom: dict[str, Any]
    model_config = {"arbitrary_types_allowed": True}

    def to_vrl(self) -> list[str]:
        lines = []
        for vrl_code in self.custom.values():
            lines.append(str(vrl_code))
        return lines

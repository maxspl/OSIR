from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel
from .VRL import parse_vrl_tag
from .actions import SetAction, TranslateAction, DeleteAction, CustomAction, Action


class PipelineStep(BaseModel):
    name:   str
    filter: Optional[str] = None


class Stage(BaseModel):
    actions: list[dict[str, Any]]
    model_config = {"arbitrary_types_allowed": True}

    def parsed_actions(self) -> list[Action]:
        result = []
        for raw in self.actions:
            raw = parse_vrl_tag(raw)
            if "set" in raw:
                result.append(SetAction(set=raw["set"], filter=raw.get("filter")))
            elif "translate" in raw:
                t = raw["translate"]
                result.append(TranslateAction(
                    mapping=t.get("mapping", {}),
                    dictionary=t.get("dictionary", {}),
                    fallback=t.get("fallback"),
                ))
            elif "delete" in raw:
                result.append(DeleteAction(delete=raw["delete"]))
            elif "custom" in raw:
                result.append(CustomAction(custom=raw["custom"]))
        return result

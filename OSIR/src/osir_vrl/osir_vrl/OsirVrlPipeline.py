from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel
from .OsirVrlUtils import parse_vrl_tag
from .actions import OsirVrlSet, OsirVrlTranslate, OsirVrlDelete, OsirVrlCustom, Action


class OsirVrlPipelineStep(BaseModel):
    name:   str
    filter: Optional[str] = None


class OsirVrlStage(BaseModel):
    actions: list[dict[str, Any]]
    model_config = {"arbitrary_types_allowed": True}

    def parsed_actions(self) -> list[Action]:
        result = []
        for raw in self.actions:
            raw = parse_vrl_tag(raw)
            if "set" in raw:
                result.append(OsirVrlSet(set=raw["set"], filter=raw.get("filter")))
            elif "translate" in raw:
                t = raw["translate"]
                result.append(OsirVrlTranslate(
                    mapping=t.get("mapping", {}),
                    dictionary=t.get("dictionary", {}),
                    fallback=t.get("fallback"),
                    filter=raw.get("filter")
                ))
            elif "delete" in raw:
                result.append(OsirVrlDelete(delete=raw["delete"],filter=raw.get("filter")))
            elif "custom" in raw:
                result.append(OsirVrlCustom(custom=raw["custom"],filter=raw.get("filter")))
        return result

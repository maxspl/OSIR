from __future__ import annotations
from pydantic import BaseModel
from .OsirVrlPipeline import OsirVrlPipelineStep, OsirVrlStage
from .OsirVrlDescription import OsirVrlDescription
from .OsirVrlField import OsirVrlField
from .actions import OsirVrlSet, OsirVrlDelete
from .OsirVrlUtils import OsirVrlVRL, extract_vrl_fields
from osir_lib.core.model.OsirMetadataModel import OsirMetadataModel

_HR = "# " + "-" * 77


class OsirVrlModel(BaseModel):
    metadata:     OsirMetadataModel
    pipeline:     list[OsirVrlPipelineStep]
    stages:       dict[str, OsirVrlStage]
    fields:       list[OsirVrlField]       = []
    descriptions: list[OsirVrlDescription] = []

    @classmethod
    def from_yaml(cls, path: str) -> "OsirVrlModel":
        import yaml
        with open(path, encoding="utf-8") as f:
            return cls.model_validate(yaml.safe_load(f))

    def to_vrl(self) -> str:
        return "\n".join([
            self._pipeline_to_vrl(),
            self._descriptions_to_vrl(),
        ])

    def save_vrl(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_vrl())

    # ── dotted field normalization ─────────────────────────────────────────────

    def _collect_dotted_source_fields(self) -> list[str]:
        seen: dict[str, bool] = {}
        for step in self.pipeline:
            if step.name not in self.stages:
                continue
            for action in self.stages[step.name].parsed_actions():
                if not isinstance(action, OsirVrlSet):
                    continue
                exprs = list(action.set.values())
                if action.filter:
                    exprs.append(action.filter)
                for val in exprs:
                    if not isinstance(val, OsirVrlVRL):
                        continue
                    for ref in extract_vrl_fields(str(val)):
                        name = ref.lstrip(".")
                        if "." in name:
                            seen[name] = True
        return list(seen.keys())

    def _normalize_dotted_fields_vrl(self) -> str:
        fields = self._collect_dotted_source_fields()
        if not fields:
            return ""
        lines = [f"\n{_HR}\n# normalize dotted fields\n{_HR}"]
        for field in fields:
            field_without_quote = field
            if '"' in field:
                field_without_quote = field.replace('"',"")
            lines.append(f'if exists(."{field_without_quote}") {{ .{field} = get!(., path: ["{field_without_quote}"]) }}')
        return "\n".join(lines)

    # ── VRL rendering ──────────────────────────────────────────────────────────

    def _pipeline_to_vrl(self) -> str:
        flat_fields = set(self._collect_dotted_source_fields())
        lines: list[str] = [self._normalize_dotted_fields_vrl()]
        for step in self.pipeline:
            if step.name not in self.stages:
                continue
            lines.append(f"\n{_HR}\n# {step.name}\n{_HR}")
            for action in self.stages[step.name].parsed_actions():
                if isinstance(action, OsirVrlDelete):
                    lines.extend(action.to_vrl(flat_fields))
                else:
                    lines.extend(action.to_vrl())
        return "\n".join(lines)

    def _descriptions_to_vrl(self) -> str:
        if not self.descriptions:
            return ""
        sorted_d = sorted(self.descriptions, key=lambda d: len(d.conditions))
        lines = [f"\n{_HR}\n# descriptions\n{_HR}"]
        for d in sorted_d:
            lines.append(d.to_vrl())
        return "\n".join(lines)

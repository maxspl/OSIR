from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, model_validator
from .OsirVrlBlock import OsirVrlBlock
from .OsirVrlTransformation import OsirVrlTransformation, is_path
from .OsirVrlTimeline import OsirVrlRelationship, OsirVrlTimelineEntry
from .OsirVrlUtils import extract_vrl_fields
from osir_lib.core.model.OsirMetadataModel import OsirMetadataModel

_HR = "# " + "-" * 77


class OsirVrlMetadata(OsirMetadataModel):
    id:   str = ""
    type: str = ""


class OsirVrlSource(BaseModel):
    model_config = {"extra": "forbid"}
    tools:    Optional[str] = None
    internal: Optional[str] = None
    raw:     Optional[str] = None


class OsirVrlModel(BaseModel):
    """Declarative VRL program: metadata + source, an ordered list of
    transformation blocks (`set` / `constant` / `translate` / `delete` /
    `custom`, each expanded linearly: first entry = first VRL
    instruction), then the timeline (id / message / conditions) and the
    relationships, each attached to a timeline element through its id."""

    model_config = {"extra": "forbid"}

    metadata:      OsirVrlMetadata
    source:        Optional[OsirVrlSource]        = None
    transformation: list[OsirVrlBlock]             = []
    timeline:      list[OsirVrlTimelineEntry]     = []
    relationships: list[OsirVrlRelationship]     = []

    @model_validator(mode="after")
    def _validate_relationship_ids(self) -> "OsirVrlModel":
        timeline_ids = [e.id for e in self.timeline if e.id]
        duplicates = {i for i in timeline_ids if timeline_ids.count(i) > 1}
        if duplicates:
            raise ValueError(f"duplicate timeline ids: {sorted(duplicates)}")
        known = set(timeline_ids)
        unknown = [r.id for r in self.relationships if r.id not in known]
        if unknown:
            raise ValueError(
                f"relationships reference unknown timeline ids: {unknown}")
        return self

    @property
    def entries(self) -> list[OsirVrlTransformation]:
        """All transformation entries, flattened in program order."""
        return [e for block in self.transformation for e in block.entries()]

    @classmethod
    def from_yaml(cls, path: str) -> "OsirVrlModel":
        import yaml
        with open(path, encoding="utf-8") as f:
            return cls.model_validate(yaml.safe_load(f))

    def to_vrl(self) -> str:
        return "\n".join([
            self._header_to_vrl(),
            self._normalize_dotted_fields_vrl(),
            self._transformations_to_vrl(),
            self._timeline_to_vrl(),
        ])

    def save_vrl(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_vrl())

    # ── header ─────────────────────────────────────────────────────────────────

    def _header_to_vrl(self) -> str:
        lines = [
            "##############################################################",
            f"# Module VRL : {self.metadata.id}",
            f"# Version    : {self.metadata.version}",
        ]
        if self.metadata.type:
            lines.append(f"# Type       : {self.metadata.type}")
        lines.append(f"# {self.metadata.description}")
        if self.source:
            parts = []
            if self.source.tools:
                parts.append(f"tools={self.source.tools}")
            if self.source.internal:
                parts.append(f"internal={self.source.internal}")
            if self.source.raw:
                parts.append(f"raw={self.source.raw}")
            if parts:
                lines.append(f"# Source     : {', '.join(parts)}")
        lines += [
            "#",
            "# Fichier généré automatiquement à partir de la configuration YAML.",
            "# Ne pas éditer directement — modifier la configuration source.",
            "##############################################################",
        ]
        return "\n".join(lines)

    # ── dotted field normalization ─────────────────────────────────────────────

    def _collect_dotted_source_fields(self) -> list[str]:
        seen: dict[str, bool] = {}
        for t in self.entries:
            exprs: list[str] = []
            # deletion sources are field names, custom blocks contain real VRL
            # paths: only VRL expression sources can reference flat dotted keys
            if t.type != "custom" and t.type != "deletion" \
                    and isinstance(t.source, str) and not is_path(t.source):
                exprs.append(t.source)
            if t.filter:
                exprs.append(t.filter)
            for expr in exprs:
                for ref in extract_vrl_fields(expr):
                    name = ref.lstrip(".")
                    if "." in name:
                        seen[name] = True
        # timeline fields: message templates and relationships reference
        # event paths that may also live behind a single flat dotted key
        # (e.g. a splunk constant injected as "user.name")
        for entry in self.timeline:
            timeline_fields: list[str] = list(entry._template_fields())
            for rel in self.relationships:
                timeline_fields += [rel.source, rel.target]
            for name in timeline_fields:
                name = name.lstrip(".")
                if "." in name:
                    seen[name] = True
        return list(seen.keys())

    def _normalize_dotted_fields_vrl(self) -> str:
        fields = self._collect_dotted_source_fields()
        if not fields:
            return ""
        lines = [f"\n{_HR}\n# normalize dotted fields\n{_HR}"]
        for field in fields:
            field_without_quote = field.replace('"', "") if '"' in field else field
            lines.append(f'if exists(."{field_without_quote}") {{')
            lines.append(f'  .{field} = get!(., path: ["{field_without_quote}"])')
            lines.append(f'  del(."{field_without_quote}")')
            lines.append('}')
        return "\n".join(lines)

    # ── transformations (linear) ────────────────────────────────────────────────

    def _transformations_to_vrl(self) -> str:
        entries = self.entries
        if not entries:
            return ""
        flat_fields = set(self._collect_dotted_source_fields())
        lines = [f"\n{_HR}\n# transformations\n{_HR}"]
        for t in entries:
            if t.type == "deletion":
                src = ", ".join(t._source_fields())
                lines.append(f"\n# [{t.type}] {src}")
            elif t.type == "custom":
                lines.append(f"\n# [{t.type}]")
            else:
                src = t.source if t.source is not None else t.value
                lines.append(f"\n# [{t.type}] {src} -> {t.target}")
            lines.extend(t.to_vrl(flat_fields, module_id=self.metadata.id))
        return "\n".join(lines)

    # ── timeline (rendered after transformations) ───────────────────────────────

    def _timeline_to_vrl(self) -> str:
        if not self.timeline:
            return ""
        rels_by_id: dict[str, list[OsirVrlRelationship]] = {}
        for rel in self.relationships:
            rels_by_id.setdefault(rel.id, []).append(rel)
        sorted_t = sorted(self.timeline, key=lambda e: len(e.conditions))
        lines = [f"\n{_HR}\n# timeline\n{_HR}"]
        for entry in sorted_t:
            lines.append(entry.to_vrl(rels_by_id.get(entry.id or "", [])))
        return "\n".join(lines)

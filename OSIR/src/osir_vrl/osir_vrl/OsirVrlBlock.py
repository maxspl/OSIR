from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, PrivateAttr, field_validator, model_validator
from .OsirVrlTimeline import OsirVrlCondition
from .OsirVrlTransformation import OsirVrlTransformation

BLOCK_KINDS = ("set", "constant", "translate", "delete", "custom")

# guards live on the block, next to its kind key, never inside an entry
_BLOCK_GUARD_KEYS = ("filter", "conditions")


class OsirVrlBlock(BaseModel):
    """One item of the `transformation` list: a typed block holding one or
    several entries, expanded (in order) into linear VRL instructions.

    Block kinds (v1 structure):
      - set:       mapping `target: spec`, spec being either a shorthand
                   string (a field path / VRL expression used as source) or
                   a mapping with `source` / `value` / `operation` /
                   `parameters` / `on_error`
      - constant:  mapping `target: value`, every spec being a literal
                   value (string, number, boolean, list) — the shorthand of
                   a `set` entry written as `{value: ...}`
      - translate: `mapping: {target: source}` + shared `dictionary` and
                   optional `fallback`
      - delete:    list of field names to `del()`
      - custom:    raw VRL code

    `filter` (raw VRL) and `conditions` (declarative, timeline semantics)
    sit at the block level, next to the kind key, and guard every entry of
    the block.

    Entries of a block are rendered in mapping order; blocks are rendered in
    list order, so the whole `transformation` list stays a linear program.
    """
    model_config = {"extra": "forbid"}
    set:       Optional[dict[str, Any]] = None
    constant:  Optional[dict[str, Any]] = None
    translate: Optional[dict[str, Any]] = None
    delete:    Optional[list[str]]      = None
    custom:    Optional[str]            = None
    # block-level guards, shared by every entry of the block
    filter:     Optional[str]          = None
    conditions: list[OsirVrlCondition] = []

    _entries: list[OsirVrlTransformation] = PrivateAttr(default_factory=list)

    @field_validator("delete", mode="before")
    @classmethod
    def _delete_to_list(cls, v: Any) -> Any:
        if isinstance(v, str):
            return [v]
        return v

    @model_validator(mode="after")
    def _validate_shape(self) -> "OsirVrlBlock":
        kinds = [k for k in BLOCK_KINDS if getattr(self, k) is not None]
        if len(kinds) != 1:
            raise ValueError(
                f"a transformation block takes exactly one of {BLOCK_KINDS}, got {kinds or 'none'}"
            )
        kind = kinds[0]
        if kind == "set":
            if not self.set:
                raise ValueError("set block takes at least one target")
            self._entries = [
                OsirVrlTransformation.model_validate({
                    "type": "normalization",
                    "target": target,
                    "filter": self.filter,
                    "conditions": self.conditions,
                    **self._entry_spec(spec),
                })
                for target, spec in self.set.items()
            ]
        elif kind == "constant":
            if not self.constant:
                raise ValueError("constant block takes at least one target")
            self._entries = [
                OsirVrlTransformation.model_validate({
                    "type": "normalization",
                    "target": target,
                    "value": spec,
                    "filter": self.filter,
                    "conditions": self.conditions,
                })
                for target, spec in self.constant.items()
            ]
        elif kind == "translate":
            self._validate_translate_shape()
        elif kind == "delete":
            if not self.delete:
                raise ValueError("delete block takes at least one field")
            self._entries = [OsirVrlTransformation(
                type="deletion", source=self.delete,
                filter=self.filter, conditions=self.conditions,
            )]
        else:
            if not self.custom:
                raise ValueError("custom block requires raw VRL code")
            self._entries = [OsirVrlTransformation(
                type="custom", source=self.custom,
                filter=self.filter, conditions=self.conditions,
            )]
        return self

    def _validate_translate_shape(self) -> None:
        """v1 translate structure: mapping + dictionary + fallback."""
        if not isinstance(self.translate, dict):
            raise ValueError("translate block takes a mapping")
        unknown = [k for k in self.translate if k not in ("mapping", "dictionary", "fallback")]
        if unknown:
            raise ValueError(
                f"translate block takes mapping/dictionary/fallback, got unknown key(s) {unknown}"
            )
        mapping = self.translate.get("mapping")
        if not isinstance(mapping, dict) or not mapping:
            raise ValueError("translate block requires a non-empty mapping: {target: source}")
        dictionary = self.translate.get("dictionary")
        fallback = self.translate.get("fallback")
        if dictionary is None:
            raise ValueError("translate block requires a dictionary")
        if fallback is not None and not isinstance(fallback, str):
            raise ValueError("translate fallback must be a string")
        self._entries = [
            OsirVrlTransformation(
                type="translation", target=target, source=source,
                dictionary=dictionary, fallback=fallback,
                filter=self.filter, conditions=self.conditions,
            )
            for target, source in mapping.items()
        ]

    # ── expansion to linear entries ─────────────────────────────────────────────

    def entries(self) -> list[OsirVrlTransformation]:
        """The block expanded into linear transformation entries, in order."""
        return self._entries

    @staticmethod
    def _entry_spec(spec: Any) -> Any:
        """Set entry shorthand: a plain string is a source (field path or VRL
        expression); literal values must use the explicit `value:` form."""
        if isinstance(spec, str):
            return {"source": spec}
        if not isinstance(spec, dict):
            raise ValueError(
                "a set entry is a source string or a mapping "
                "(source/value/operation/parameters/on_error)"
            )
        for k in _BLOCK_GUARD_KEYS:
            if k in spec:
                raise ValueError(
                    f"a set entry takes no {k}: {k} is block-level, on the set block itself"
                )
        return spec

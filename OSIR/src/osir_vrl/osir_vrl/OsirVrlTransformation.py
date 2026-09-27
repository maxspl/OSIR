from __future__ import annotations
import re
from typing import Any, Optional
from pydantic import BaseModel, field_validator, model_validator
from .OsirVrlTimeline import OsirVrlCondition
from .OsirVrlUtils import condition_guard, extract_vrl_fields, render_value

TRANSFORMATION_TYPES = ("normalization", "translation", "deletion", "transformation", "custom")
ON_ERROR_MODES = ("log", "direct")
# VRL functions that are infallible whatever their arguments: they cannot be
# destructured (`_r, err = now()` is compile error E104), so they are always
# rendered as a direct call. Extend this set if the compiler reports E104.
INFALLIBLE_OPERATIONS = frozenset({
    "now",
    "uuid_v4",
    "encode_json",
})

# A plain dotted field path: `type`, `.type`, `.Event.System.TimeCreated."#attributes".SystemTime`
_PATH_RE = re.compile(
    r'''^\.?(?:[A-Za-z_@][A-Za-z0-9_@-]*|\."[^"]+")(?:\.(?:[A-Za-z_@][A-Za-z0-9_@-]*|\."[^"]+"))*$'''
)
_VTAG_PREFIXES = ("v'", 'v"', "v|", "v>")


def is_path(value: Any) -> bool:
    """True when a source is a plain dotted field path (as opposed to a VRL expression)."""
    return isinstance(value, str) and bool(_PATH_RE.match(value))


class OsirVrlTransformation(BaseModel):
    """One linear transformation step: the first item of `transformations`
    is the first VRL instruction, the second the second, and so on.

    A `source` is either a dotted field path (guarded by exists(), rendered
    as `.path`) or a raw VRL expression (rendered verbatim, guarded on the
    fields it references). Use `value` for literal values instead.

    Types (mostly inferred):

      - normalization / transformation (default): `.target = operation(source, parameters...)`, `.target = source` or `.target = value`
      - translation (inferred from `dictionary`/`fallback`): `.target = get(value: dictionary, path: [to_string(source)]) ?? fallback`
      - deletion (inferred when no `target`): `del(.source)` per field
      - custom (explicit): raw VRL code in `source` (escape hatch)

    Guards: an entry is rendered inside `if <guard> { ... }` combining, in
    order, the raw VRL `filter`, the declarative `conditions` (timeline
    semantics: no value -> exists(), otherwise equality) and the default
    source guards.

    Error handling (default): VRL functions taking an event field (type `any`)
    are fallible at compile time, so an `operation` is by default rendered with
    the non-aborting error-handling pattern::

        _result, err = operation(...)
        if err == null {
            .target = _result
        } else {
            log("[module] échec ... : " + err, level: "warn")
        }

    Opt-outs:

      - `operation: downcase!` (bang variant): aborting call, rendered verbatim
      - operation listed in INFALLIBLE_OPERATIONS: direct call (destructured calls on infallible functions are compile error E104)
      - `on_error: direct`: render the call verbatim (escape hatch)
    """
    model_config = {"extra": "forbid"}
    target:     Optional[str]           = None
    type:       Optional[str]           = None
    source:     Any                     = None
    value:      Any                     = None
    operation:  Optional[str]           = None
    parameters: dict[str, Any]           = {}
    on_error:   Optional[str]           = None
    filter:     Optional[str]           = None
    conditions: list[OsirVrlCondition]  = []
    dictionary: Optional[dict[str, str]] = None
    fallback:   Optional[str]           = None

    @field_validator("dictionary", mode="before")
    @classmethod
    def _coerce_dictionary_keys(cls, v: Any) -> Any:
        # YAML maps with numeric keys (`1100: ...`) load as ints: coerce to
        # strings, since the VRL lookup is done on to_string!(source).
        if isinstance(v, dict):
            return {str(k): val for k, val in v.items()}
        return v

    @model_validator(mode="after")
    def _validate_shape(self) -> "OsirVrlTransformation":
        # v-tags are gone: catch leftover v'...' values with a clear message
        for field in ("source", "filter"):
            val = getattr(self, field)
            if isinstance(val, str) and val[:2] in _VTAG_PREFIXES:
                raise ValueError(
                    f"{field} still uses a v-tag ({val[:2]}...): v-tags were removed, "
                    "write the dotted path or the VRL expression directly"
                )
        # type inference
        if self.type is None:
            if self.target is None and self.source is not None:
                self.type = "deletion"
            elif self.dictionary is not None or self.fallback is not None:
                self.type = "translation"
            else:
                self.type = "normalization"
        if self.type not in TRANSFORMATION_TYPES:
            raise ValueError(
                f"unknown transformation type '{self.type}', expected one of {TRANSFORMATION_TYPES}"
            )
        if self.source is not None and self.value is not None:
            raise ValueError("source and value are mutually exclusive")
        if self.type == "deletion":
            if not self.source:
                raise ValueError("deletion transformation requires a source")
            if self.target is not None or self.value is not None:
                raise ValueError("deletion transformation takes no target/value")
        elif self.type == "custom":
            if not self.source or not isinstance(self.source, str):
                raise ValueError("custom transformation requires raw VRL code in source")
        else:
            if not self.target:
                raise ValueError(f"{self.type} transformation requires a target")
            if self.source is not None and not isinstance(self.source, (str, list)):
                raise ValueError(f"{self.type} source must be a field path or a VRL expression")
            if self.type == "translation":
                if not self.source or not isinstance(self.source, str):
                    raise ValueError("translation requires a field path / expression source")
                if self.value is not None:
                    raise ValueError("translation takes a source, not a value")
            else:
                if self.source is not None and isinstance(self.source, list):
                    raise ValueError("list sources are only valid for deletion")
                if self.source is None and self.value is None and self.operation is None:
                    raise ValueError(f"{self.type} transformation requires a source or a value")
        if self.on_error is not None:
            if self.on_error not in ON_ERROR_MODES:
                raise ValueError(
                    f"unknown on_error mode '{self.on_error}', expected one of {ON_ERROR_MODES}"
                )
            if not self.operation:
                raise ValueError("on_error requires an operation")
            if self.on_error == "log" and self._base_operation() in INFALLIBLE_OPERATIONS:
                raise ValueError(
                    f"on_error: log is not applicable to infallible operation "
                    f"'{self._base_operation()}' (compile error E104); use on_error: direct"
                )
        return self

    def to_vrl(self, flat_fields: set[str] = frozenset(), module_id: str = "") -> list[str]:
        if self.type == "deletion":
            # del() is infallible on a missing path: no default guard, so that
            # each field of a list is deleted independently of the others.
            return self._wrap_in_guard(self._deletion_lines(flat_fields), guard_default=False)
        if self.type == "translation":
            return self._wrap_in_guard(self._translation_lines(module_id))
        if self.type == "custom":
            return self._wrap_in_guard(self._custom_lines(), guard_default=False)
        return self._wrap_in_guard(self._assignment_lines(module_id))

    # ── helpers ───────────────────────────────────────────────────────────────

    def _base_operation(self) -> Optional[str]:
        """Operation name without its bang suffix."""
        if not self.operation:
            return None
        return self.operation[:-1] if self.operation.endswith("!") else self.operation

    def _effective_on_error(self) -> str:
        """Resolve how an operation call is rendered:
        - "log": non-aborting `_result, err` pattern (default for fallible calls)
        - "direct": verbatim call
        """
        if self.on_error:
            return self.on_error
        if self.operation and self.operation.endswith("!"):
            return "direct"
        if self._base_operation() in INFALLIBLE_OPERATIONS:
            return "direct"
        return "log"

    def _source_fields(self) -> list[str]:
        """Source as a list of dotted field names (plain fields only)."""
        if self.source is None:
            return []
        if isinstance(self.source, list):
            return [str(s) for s in self.source]
        return [str(self.source)]

    def _field_path(self, field: str) -> str:
        """VRL event path for a dotted field: .a.b or ."a b"."""
        if " " in field:
            return f'."{field}"'
        return f".{field}" if not field.startswith(".") else field

    def _source_expr(self) -> Optional[str]:
        """Source rendered as a VRL value: path -> .path, expression -> verbatim."""
        if self.source is None or isinstance(self.source, list):
            return None
        if is_path(self.source):
            return self._field_path(str(self.source))
        return str(self.source)

    def _guard(self, default: bool) -> Optional[str]:
        """Guard combining the explicit filter, the declarative conditions
        (timeline semantics) and the default source guards (same semantics
        as the legacy nested `if filter { if exists(...) }`).

        A default source guard is skipped when the filter/conditions already
        cover it (positive `exists(.ref)` only: `!exists(.ref)` does not
        count), so `filter: exists(.x) && !exists(.y)` on source `x` renders
        without a duplicated `exists(.x)`."""
        parts: list[str] = []
        if self.filter:
            parts.append(str(self.filter))
        for c in self.conditions:
            parts.append(condition_guard(c.field, c.value, c.exists))
        if default and self.source is not None and not isinstance(self.source, list):
            src = self._source_expr()
            if src is not None:
                if is_path(self.source):
                    default_guards = [f"exists({src})"]
                else:
                    default_guards = [f"exists({ref})" for ref in extract_vrl_fields(src)]
                covered = " && ".join(parts)
                for g in default_guards:
                    # positive match only: skip `!exists(...)` (lookbehind)
                    if not re.search(r"(?<![!\w])" + re.escape(g), covered):
                        parts.append(g)
        if not parts:
            return None
        return " && ".join(parts)

    def _wrap_in_guard(self, lines: list[str], guard_default: bool = True) -> list[str]:
        guard = self._guard(guard_default)
        if not guard:
            return lines
        return [f"if {guard} {{"] + [f"  {line}" for line in lines] + ["}"]

    # ── per-type rendering ─────────────────────────────────────────────────────

    def _operation_call(self) -> str:
        args: list[str] = []
        if self.value is not None:
            args.append(render_value(self.value))
        else:
            src_arg = self._source_expr()
            if src_arg:
                args.append(src_arg)
        for key, val in self.parameters.items():
            args.append(f"{key}: {render_value(val)}")
        op = self.operation
        if self._effective_on_error() == "log" and op.endswith("!"):
            op = op[:-1]
        return f"{op}({', '.join(args)})"

    def _assignment_lines(self, module_id: str = "") -> list[str]:
        target = self._field_path(self.target)
        if self.operation:
            if self._effective_on_error() == "log":
                op = self._base_operation()
                prefix = f"[{module_id}] " if module_id else ""
                return [
                    f"_result, err = {self._operation_call()}",
                    "if err == null {",
                    f"  {target} = _result",
                    "} else {",
                    f"  log(\"{prefix}échec de l'opération {op} sur {self.target} : \" + err, level: \"warn\")",
                    "}",
                ]
            return [f"{target} = {self._operation_call()}"]
        if self.value is not None:
            return [f"{target} = {render_value(self.value)}"]
        expr = self._source_expr()
        return [f"{target} = {expr}"]

    def _translation_lines(self, module_id: str = "") -> list[str]:
        src = self._source_expr()
        dictionary = self.dictionary or {}
        dict_literal = "{\n" + "".join(
            f'  "{k}": "{v}",\n' for k, v in dictionary.items()
        ) + "}"
        call = f"get(value: {dict_literal}, path: [to_string!({src})])"
        target = self._field_path(self.target)
        if self.fallback is not None:
            return [f"{target} = {call} ?? \"{self.fallback}\""]
        # no fallback: get() is fallible (value is `any`), assign on success
        # and log a warning otherwise instead of aborting
        prefix = f"[{module_id}] " if module_id else ""
        return [
            f"_result, err = {call}",
            "if err == null {",
            f"  {target} = _result",
            "} else {",
            f"  log(\"{prefix}échec de l'opération get sur {self.target} : \" + err, level: \"warn\")",
            "}",
        ]

    def _deletion_lines(self, flat_fields: set[str]) -> list[str]:
        lines = []
        for field in self._source_fields():
            if " " in field:
                lines.append(f'del(."{field}")')
            elif "." in field and field in flat_fields:
                lines.append(f'del(."{field}")')
            else:
                lines.append(f"del({self._field_path(field)})")
        return lines

    def _custom_lines(self) -> list[str]:
        return [line for line in str(self.source).splitlines()]

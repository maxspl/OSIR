from __future__ import annotations
from typing import Optional, Union
from pydantic import BaseModel
from ..VRL import VRL


class TranslateAction(BaseModel):
    mapping:    dict[str, str]
    dictionary: dict[Union[str, int], str]
    fallback:   Optional[str] = None
    filter:     Optional[VRL] = None
    model_config = {"arbitrary_types_allowed": True}

    def to_vrl(self) -> list[str]:
        if self.filter:
            lines = [f"if {self.filter} {{"]
            for dst_field, src_field in self.mapping.items():
                lines.extend(self._stmt_lines(dst_field, src_field, indent="  "))
            lines.append("}")
            return lines

        lines = []
        for dst_field, src_field in self.mapping.items():
            lines.extend(self._stmt_lines(dst_field, src_field))
        return lines

    def _stmt_lines(self, dst_field: str, src_field: str, indent: str = "") -> list[str]:
        src          = src_field if src_field.startswith(".") else f".{src_field}"
        dict_literal = "{\n" + "".join(
            f'{indent}  "{k}": "{v}",\n' for k, v in self.dictionary.items()
        ) + f"{indent}}}"
        fallback = f' ?? "{self.fallback}"' if self.fallback else ""
        return [f"{indent}.{dst_field} = get(value: {dict_literal}, path: [to_string!({src})]){fallback}"]

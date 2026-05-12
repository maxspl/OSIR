from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class TranslateAction(BaseModel):
    mapping:    dict[str, str]
    dictionary: dict[str, str]
    fallback:   Optional[str] = None

    def to_vrl(self) -> list[str]:
        lines = []
        for dst_field, src_field in self.mapping.items():
            src          = src_field if src_field.startswith(".") else f".{src_field}"
            dict_literal = "{\n" + "".join(
                f'  "{k}": "{v}",\n' for k, v in self.dictionary.items()
            ) + "}"
            fallback = f' ?? "{self.fallback}"' if self.fallback else ""
            lines.append(f'.{dst_field} = get(value: {dict_literal}, path: [{src}]){fallback}')
        return lines

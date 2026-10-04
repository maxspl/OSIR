from typing import List, Optional

from pydantic import BaseModel, model_validator


class OsirExtractedEntry(BaseModel):
    """One named extraction from the module input path.

    Declared in the module YAML under `extracted` as a single-key list
    item, the key being the extraction name:

        extracted:
          - endpoint:
              patterns:
                - r"restore_fs\\/(.*?)\\/"
              default: "UNKNOWN"
          - user:
              patterns:
                - r"Users\\/([^\\/]+)"
              default: "UNKNOWN"

    `patterns` are tried in order against the input path (first capture
    group wins); `default` is the fallback when no pattern matches.
    """
    name: str
    patterns: Optional[List[str]] = None
    default: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _from_single_key_mapping(cls, data):
        """Accept the YAML shape `- <name>: {patterns, default}`."""
        if isinstance(data, dict) and "name" not in data and len(data) == 1:
            (name, spec), = data.items()
            if isinstance(spec, dict):
                return {"name": name, **spec}
        return data

    @model_validator(mode="after")
    def at_least_one_field_set(self) -> "OsirExtractedEntry":
        if not self.patterns and not self.default:
            raise ValueError(
                f"extraction '{self.name}': at least one of 'patterns' or 'default' must be set"
            )
        return self

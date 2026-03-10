from typing import List, Optional

from pydantic import BaseModel, model_validator

class OsirEndpointModel(BaseModel):
    """
    Data model defining the structure and validation for OSIR endpoint configuration.
    At least one of `patterns` or `default` must be set.
    """
    patterns: Optional[List[str]] = None
    default: Optional[str] = None

    @model_validator(mode='after')
    def at_least_one_field_set(self) -> "OsirEndpointModel":
        if not self.patterns and not self.default:
            raise ValueError("At least one of 'patterns' or 'default' must be set")
        return self
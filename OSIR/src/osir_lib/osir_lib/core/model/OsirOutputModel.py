from pathlib import Path
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class OsirOutputModel(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    type: Optional[str] = None
    format:  Optional[str] = None
    output_dir: Optional[str] = None
    output_file: Optional[str] = None
    output_prefix: Optional[str] = None

    @field_validator("output_dir", "output_file", mode="before")
    @classmethod
    def cast_path_to_str(cls, v):
        if isinstance(v, Path):
            return str(v)
        return v
    
    @model_validator(mode="after")
    def check_prefix_usage(self) -> "OsirOutputModel":
        # Vérifie si un préfixe est fourni
        if self.output_prefix is not None:
            # Si le type n'est pas 'multiple_files', on lève une erreur
            if self.type != "multiple_files":
                raise ValueError(
                    f"output_prefix can only be used when type is 'multiple_files' (current type: '{self.type}')"
                )
        return self
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from osir_lib.core.model.LiteralModel import OUTPUT_TYPE


class OsirOutputModel(BaseModel):
    """
        Data model defining the structure and validation for forensic tool outputs.

        Attributes:
            type (str): The category of output (e.g., 'file', 'dir', 'multiple_files').
            format (str): The data format of the result (e.g., 'json', 'csv', 'txt').
            output_dir (str): The target directory for the results.
            output_file (str): The specific filename for the result.
            output_prefix (str): An optional prefix applied to all files in 
                'multiple_files' mode to avoid naming collisions.
    """
    model_config = ConfigDict(validate_assignment=True)

    type: Optional[OUTPUT_TYPE] = None
    format: Optional[str] = None
    output_dir: Optional[str] = None
    output_file: Optional[str] = None
    output_prefix: Optional[str] = None

    @field_validator("output_dir", "output_file", mode="before")
    @classmethod
    def cast_path_to_str(cls, v):
        """
            Ensures that Path objects are converted to strings before validation.

            This normalization step is necessary to ensure compatibility with 
            downstream regex and template substitution logic that expects 
            string-based path manipulation.
        """
        if isinstance(v, Path):
            return str(v)
        return v

    @model_validator(mode="after")
    def check_prefix_usage(self) -> "OsirOutputModel":
        """
            Validates the logical consistency of the output configuration.

            Ensures that the 'output_prefix' attribute is only utilized when 
            the output type is set to 'multiple_files'. This prevents 
            configuration errors where a user might expect file renaming on 
            a single-file output type.

            Raises:
                ValueError: If output_prefix is used with an incompatible output type.
        """
        if self.output_prefix is not None:
            if self.type != "multiple_files":
                raise ValueError(
                    f"output_prefix can only be used when type is 'multiple_files' "
                    f"(current type: '{self.type}')"
                )
        return self

    @property
    def file(self):
        return self.output_file

    @property
    def dir(self):
        return self.output_dir
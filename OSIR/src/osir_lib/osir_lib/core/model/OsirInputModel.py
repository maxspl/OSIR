from pathlib import Path
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from osir_lib.core.model.LiteralModel import INPUT_TYPE


class OsirInputModel(BaseModel):
    """
        Base data model defining the structure of forensic inputs in the OSIR framework.

        Attributes:
            type (INPUT_TYPE): The method used to identify the input (e.g., 'file', 'dir', 'glob').
            path (str, optional): Legacy absolute path to the data source.
            name (str, optional): Descriptive name for the input source.
            file (str, optional): Specific filename to be targeted within a directory.
            dir (str, optional): Specific directory path to be scanned.
            paths (list[str], optional): A collection of multiple paths for batch processing.
            match (Path, optional): The resolved filesystem path resulting from a successful 
                pattern match or discovery process.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    type: INPUT_TYPE

    # LEGACY FIELDS - Maintained for backward compatibility with older module definitions
    path: Optional[str] = None
    name: Optional[str] = None
    file: Optional[str] = None
    dir: Optional[str] = None

    # MODERN FIELDS - Used by the current orchestration engine for dynamic discovery
    paths: Optional[list[str]] = None
    match: Optional[Path] = None

import yaml
import os
from typing import Optional, Literal, Pattern
from pydantic import BaseModel, ValidationError

from osir_lib.core.FileManager import FileManager
from osir_lib.core.model.LiteralModel import MODULE_TYPE, OS_TYPE, PROCESSOR_OS, PROCESSOR_TYPE
from osir_lib.core.model.OsirInputModel import OsirInputModel
from osir_lib.core.model.OsirOutputModel import OsirOutputModel
from osir_lib.core.model.OsirToolModel import OsirToolModel
from osir_lib.core.model.connector.OsirConnectorModel import OsirConnectorModel

class OsirModuleModel(BaseModel):
    version: float | str
    author: str
    module: str
    description: str
    os: OS_TYPE
    type: MODULE_TYPE
    disk_only: bool
    no_multithread: bool
    processor_type: list[PROCESSOR_TYPE]
    processor_os: PROCESSOR_OS
    optional: Optional[dict] = None
    alt_module: Optional[str] = None
    env: Optional[list[str]] = None
    tool: Optional[OsirToolModel] = None
    input: OsirInputModel
    output: OsirOutputModel 
    endpoint: Optional[Pattern] = None
    connector: Optional[OsirConnectorModel] = None

    @classmethod
    def from_yaml(cls, path: str) -> "OsirModuleModel":
        """
        Load and validate an OSIR module from a YAML file.

        Raises:
            FileNotFoundError: if the YAML file does not exist
            ValidationError: if the data does not conform to the schema
        """
        
        if not os.path.isfile(path):
            raise FileNotFoundError(f"YAML file not found: {path}")
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Ensure the YAML actually contains a dict
            if not isinstance(data, dict):
                raise ValueError(f"YAML content must be a dictionary, got {type(data)}")

            return cls(**data)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML file {path}: {e}") from e
        except ValidationError as e:
            raise ValueError(f"Data validation error for module {path}: {e}") from e

    @classmethod
    def from_name(cls, name: str) -> "OsirModuleModel":
        """
        Load and validate an OSIR module from a YAML file.

        Raises:
            FileNotFoundError: if the YAML file does not exist
            ValidationError: if the data does not conform to the schema
        """
        path = FileManager.get_module_path(name)

        return cls(**OsirModuleModel.from_yaml(path=path).model_dump())

    def get_module_name(self):
        """
        Retrieves the name of the module.

        Returns:
            str: The module name.
        """
        return self.module
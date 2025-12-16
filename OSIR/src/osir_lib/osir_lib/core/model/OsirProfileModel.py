import os
from typing import Optional
from pydantic import BaseModel, ValidationError
import yaml

from osir_lib.core.FileManager import FileManager

class OsirProfileModel(BaseModel):
    version: Optional[float] = None
    author: Optional[str] = None
    description: Optional[str] = None
    os: Optional[str] = None
    modules: list[str]

    @classmethod
    def from_yaml(cls, path: str) -> "OsirProfileModel":
        """
        Load and validate an OSIR Profile from a YAML file.

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
            raise ValueError(f"Data validation error for module: {e}") from e
    
    @classmethod
    def from_name(cls, name: str) -> "OsirProfileModel":
        """
        Load and validate an OSIR module from a YAML file.

        Raises:
            FileNotFoundError: if the YAML file does not exist
            ValidationError: if the data does not conform to the schema
        """
        path = FileManager.get_profile_path(name)

        return cls(**OsirProfileModel.from_yaml(path=path).model_dump())
    
    def add_modules(self, modules: list[str]) -> None:
        modules = [item + ".yml" if not item.endswith(".yml") else item for item in modules]
        if self.modules is None:
            self.modules = []
        self.modules = list(set(self.modules).union(modules))

    def remove_modules(self, modules: list[str]) -> None:
        modules = [item + ".yml" if not item.endswith(".yml") else item for item in modules]
        if self.modules is None:
            self.modules = []
        self.modules = list(set(self.modules) - set(modules))
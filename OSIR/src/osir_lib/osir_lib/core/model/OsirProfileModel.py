import os
from typing import Optional
from pydantic import BaseModel, ValidationError
import yaml

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
        
    def add_modules(self, modules: list[str]):
        modules = [item + ".yml" if not item.endswith(".yml") else item for item in modules]
        self.modules = list(set(self.modules) + set(modules))
    
    def remove_modules(self, modules: list[str]):
        modules = [item + ".yml" if not item.endswith(".yml") else item for item in modules]
        self.modules = list(set(self.modules) - set(modules))
import os
from typing import Optional
from pydantic import BaseModel, ValidationError
import yaml

from osir_lib.core.FileManager import FileManager


class OsirProfileModel(BaseModel):
    """
        Data model representing a forensic triage profile in the OSIR framework.

        A Profile acts as a container for a list of forensic modules. It allows 
        investigators to define a specific triage logic (e.g., 'Quick Windows Triage') 
        by grouping multiple module YAMLs together. This model handles the 
        validation of the profile structure and the dynamic management of its module list.

        Attributes:
            version (float, optional): The version of the profile definition.
            author (str, optional): The creator of the profile.
            description (str, optional): A summary of the forensic goals of this profile.
            os (str, optional): The target operating system for this profile.
            modules (list[str]): A list of module filenames included in this profile.
    """
    version: Optional[float] = None
    author: Optional[str] = None
    description: Optional[str] = None
    os: Optional[str] = None
    modules: list[str]

    @classmethod
    def from_yaml(cls, path: str) -> "OsirProfileModel":
        """
            Loads and validates an OSIR Profile from a physical YAML file.

            Args:
                path (str): The filesystem path to the profile configuration file.

            Returns:
                OsirProfileModel: A validated instance of the profile.

            Raises:
                FileNotFoundError: If the YAML file is missing.
                ValueError: If the YAML is malformed or does not match the schema.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"YAML file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

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
            Loads a profile by its identifier name using the FileManager.

            Args:
                name (str): The name of the profile (e.g., 'full_triage').

            Returns:
                OsirProfileModel: The validated profile model.
        """
        path = FileManager.get_profile_path(name)
        return cls(**OsirProfileModel.from_yaml(path=path).model_dump())

    def add_modules(self, modules: list[str]) -> None:
        """
            Dynamically appends new modules to the existing profile.

            Args:
                modules (list[str]): List of module names to add.
        """
        modules = [item + ".yml" if not item.endswith(".yml") else item for item in modules]
        if self.modules is None:
            self.modules = []
        self.modules = list(set(self.modules).union(modules))

    def remove_modules(self, modules: list[str]) -> None:
        """
            Removes specific modules from the profile.

            Args:
                modules (list[str]): List of module names to remove.
        """
        modules = [item + ".yml" if not item.endswith(".yml") else item for item in modules]
        if self.modules is None:
            self.modules = []
        self.modules = list(set(self.modules) - set(modules))

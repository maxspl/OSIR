from pathlib import Path
from typing import Optional

from pydantic import model_validator
from osir_lib.core.FileManager import FileManager
from osir_lib.core.model.OsirProfileModel import OsirProfileModel
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_service.ipc.OsirIpcModel import OsirIpcModel


class OsirIpc(OsirIpcModel):
    """
        Functional implementation of an IPC request within the OSIR IPC service.

        Attributes:
            modules_instance (Optional[list[OsirModuleModel]]): A list of forensic modules model.
            profile (Optional[OsirProfileModel]): The validated profile object 
                if a profile-based execution was requested.
            case_path (Optional[Path]): The resolved absolute path to the 
                investigation case directory.
    """
    modules_instance: Optional[list[OsirModuleModel]] = None
    profile: Optional[OsirProfileModel] = None
    case_path: Optional[Path] = None

    @model_validator(mode='before')
    @classmethod
    def transform_input_data(cls, data: dict) -> dict:
        """
        Pre-validation hook to transform input strings into complex models.

        Args:
            data (dict): The raw input dictionary before Pydantic validation.

        Returns:
            dict: The transformed data dictionary.
        """
        # Resolve Profile: string name -> OsirProfileModel instance
        profile_value = data.get("profile")
        if isinstance(profile_value, str):
            data["profile"] = OsirProfileModel.from_name(profile_value)

        return data

    def __init__(self, **data):
        """
        Initializes the IPC request and hydrates nested forensic components.
        """
        super().__init__(**data)

        # Ensure profile hydration if it remained a string
        if isinstance(self.profile, str):
            self.profile = OsirProfileModel.from_name(self.profile)

        # Load each individual module YAML into a validated Module Model
        if self.modules:
            self.modules_instance: list[OsirModuleModel] = [
                OsirModuleModel.from_yaml(FileManager.get_module_path(module))
                for module in self.modules
            ]

        # Map the case name to its storage location on the Master node
        if self.case_name:
            self.case_path = FileManager.get_cases_path(self.case_name)

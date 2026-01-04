from pathlib import Path
from typing import Optional

from pydantic import model_validator
from osir_lib.core.FileManager import FileManager
from osir_lib.core.model.OsirProfileModel import OsirProfileModel
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_service.ipc.OsirIpcModel import OsirIpcModel

class OsirIpc(OsirIpcModel):
    modules_instance: Optional[list[OsirModuleModel]] = None
    profile: Optional[OsirProfileModel] = None
    case_path: Optional[Path] = None

    @model_validator(mode='before')
    @classmethod
    def transform_input_data(cls, data: dict) -> dict:
        """Transforme les inputs (str) en instances de modèles avant la validation."""
        
        # 1. Gestion du profile : str -> OsirProfileModel
        profile_value = data.get("profile")
        if isinstance(profile_value, str):
            data["profile"] = OsirProfileModel.from_name(profile_value)
        
        return data

    def __init__(self, **data):
        super().__init__(**data)

        if isinstance(self.profile, str):
            self.profile = OsirProfileModel.from_name(self.profile)

        if self.modules:
            self.modules_instance: list[OsirModuleModel] = [
                OsirModuleModel.from_yaml(FileManager.get_module_path(module))
                for module in self.modules
            ]

        if self.case_name:
            self.case_path = FileManager.get_cases_path(self.case_name)
            # if self.case_path is None:
            #     raise ValueError(f"The case path for '{self.case_name}' does not exist or could not be found.")
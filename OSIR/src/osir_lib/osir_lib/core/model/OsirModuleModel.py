import importlib
import inspect
from pathlib import Path
import pkgutil
import sys
import yaml
import os
from typing import Callable, Optional, Literal, Pattern
from pydantic import BaseModel, ValidationError, model_validator

from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.core.model.LiteralModel import MODULE_TYPE, OS_TYPE, PROCESSOR_OS, PROCESSOR_TYPE
from osir_lib.core.model.OsirInputModel import OsirInputModel
from osir_lib.core.model.OsirOutputModel import OsirOutputModel
from osir_lib.core.model.OsirToolModel import OsirToolModel
from osir_lib.core.model.connector.OsirConnectorModel import OsirConnectorModel
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()

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

    # TODO: REMOVE LEGACY
    splunk: Optional[dict] = None
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
        return self.module_name
    
    @property
    def module_name(self):
        return self.module
    
    def find_and_load_internal_module(self, alt_module=None) -> Optional[Callable]:
        """
        Recherche récursivement un fichier module_name.py et retourne la fonction/classe
        décorée avec @osir_internal_module.
        """
        # Utilisation du glob pattern pour la recherche récursive
        # On cherche précisément "nom_du_module.py"
        module_name = alt_module if alt_module else self.module_name

        root_path = Path(OSIR_PATHS.PY_MODULES_DIR)

        target_file = next(root_path.rglob(f"{module_name}.py"), None)

        if not target_file:
            print(f"Fichier {module_name}.py non trouvé dans {root_path}")
            return None

        try:
            # Chargement dynamique du module Python
            spec = importlib.util.spec_from_file_location(module_name, target_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                # Ajout au sys.modules pour éviter les problèmes d'imports relatifs
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                # Parcourir les attributs du module pour trouver celui décoré
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    # On vérifie la présence de l'attribut injecté par le décorateur
                    if getattr(attr, "__osir_internal__", False):
                        return attr

        except Exception as e:
            print(f"Erreur lors du chargement du module {target_file}: {e}")
        
        return None


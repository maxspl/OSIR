import importlib
from pathlib import Path
import sys
import yaml
import os
from typing import Callable, Optional, Pattern
from pydantic import BaseModel, PrivateAttr, ValidationError

from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.core.model.OsirEndpointModel import OsirEndpointModel
from osir_lib.core.model.OsirInputModel import OsirInputModel
from osir_lib.core.model.OsirOutputModel import OsirOutputModel
from osir_lib.core.model.OsirToolModel import OsirToolModel
from osir_lib.core.model.OsirMetadataModel import OsirMetadataModel
from osir_lib.core.model.OsirConfigurationModel import OsirConfigurationModel
from osir_lib.core.model.connector.OsirConnectorModel import OsirConnectorModel
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()


class OsirModuleModel(BaseModel):
    """
        Data model defining the structure and validation for OSIR modules.

        This model serves as the blueprint for all modules within the framework. 
        It validates metadata (author, version), execution requirements (OS, 
        processor type), and the core components of the task (tool, 
        input, output, and connectors).
    """
    metadata: OsirMetadataModel
    configuration: OsirConfigurationModel
    optional: Optional[dict] = None
    env: Optional[list[str]] = None
    tool: Optional[OsirToolModel] = None
    input: OsirInputModel
    output: OsirOutputModel
    endpoint: Optional[OsirEndpointModel] = None
    connector: Optional[OsirConnectorModel] = None
    
    # TODO: REMOVE LEGACY
    splunk: Optional[dict] = None

    # Private Attribute 
    filename: Optional[str] = None
    _mod_path: str = PrivateAttr(default=None)
    _rel_path: str = PrivateAttr(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        self._mod_path = FileManager.get_module_path(self.filename)
        self._rel_path = str(Path(self._mod_path).relative_to(OSIR_PATHS.MODULES_DIR))

    @classmethod
    def from_yaml(cls, path: str) -> "OsirModuleModel":
        """
            Loads and validates an OSIR module from a physical YAML file.

            This method reads the module definition and ensures it conforms to 
            the Pydantic schema before instantiation.

            Args:
                path (str): The filesystem path to the .yml module file.

            Returns:
                OsirModuleModel: A validated model instance.

            Raises:
                FileNotFoundError: If the YAML file is missing.
                ValueError: If the YAML content is malformed or invalid.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"YAML file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                data['filename'] = os.path.basename(path)
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
            Loads a module by its identifier name.

            Uses the FileManager to resolve the module's name into a physical 
            filesystem path before loading.

            Args:
                name (str): The name of the module (e.g., 'mft', 'prefetch').
        """
        path = FileManager.get_module_path(name)
        return cls(**OsirModuleModel.from_yaml(path=path).model_dump())

    def get_module_name(self):
        """
            Returns the unique identifier of the module.
        """
        return self.module_name

    @property
    def module_name(self):
        return self.configuration.module

    def find_and_load_internal_module(self, alt_module=None) -> Optional[Callable]:
        """
            Recursively locates and dynamically loads internal Python module logic.

            If a module is marked as 'internal', this method searches for a 
            corresponding .py file in the PY_MODULES_DIR. It specifically looks 
            for a class or function decorated with @osir_internal_module (identified 
            by the __osir_internal__ attribute).

            Args:
                alt_module (str, optional): An alternative module name to search for.

            Returns:
                Optional[Callable]: The decorated executable logic, or None if not found.
        """
        # Define the module name to search for
        module_name = alt_module if alt_module else self.module_name
        root_path = Path(OSIR_PATHS.PY_MODULES_DIR)

        # Recursive search for the Python source file
        target_file = next(root_path.rglob(f"{module_name}.py"), None)

        if not target_file:
            logger.error(f"File {module_name}.py not found in {root_path}")
            return None

        try:
            # Dynamic import logic
            spec = importlib.util.spec_from_file_location(module_name, target_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                # Inject into sys.modules to handle relative imports within the library
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                # Scan module attributes for the OSIR internal decorator marker
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if getattr(attr, "__osir_internal__", False):
                        return attr

        except Exception as e:
            logger.error(f"Error while loading internal module {target_file}: {e}")

        return None

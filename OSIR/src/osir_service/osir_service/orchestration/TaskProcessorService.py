import os
import pkgutil
import importlib
import traceback

from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.core.PyModule import PyModule
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger
       
logger = AppLogger(__name__).get_logger()

class ExternalProcessor:
    """
    Handles the external processing of files based on the configuration of a specific module instance.
    """
    def __init__(self, case_path: str, module_instance: OsirModule) -> None:
        """
        Initializes an ExternalProcessor instance with specified case path and module.

        Args:
            case_path (str): Path where case files are stored and operations are performed.
            module_instance (OsirModule): The module instance defining the processing rules.
        """
   
        # Declare module class from config string
        self._module_instance = module_instance
        self._py_module = PyModule(case_path, module_instance)

    def run_module(self):
        """
        Executes the external tool associated with the module instance.
        """
        self._py_module.run_ext_tool()

class InternalProcessor:
    """
    Manages the execution of internal processing tasks within a Python environment, using predefined module instances.
    """
    def __init__(self, case_path: str, module_instance: OsirModule) -> None:
        """
        Initializes the InternalProcessor with a specific case path and module instance.

        Args:
            case_path (str): The base path where case files are stored and operations are performed.
            module_instance (BaseModule): The module instance defining the processing rules and configurations.
        """
        self._module_instance = module_instance

        self.case_path = case_path  # Base directory for operations

        self.current_module = self._module_instance.get_module_name()
        self._py_module: PyModule = self.load_module()

        if not self._py_module:
            self.available = False
            logger.error(f"selected module not found {self._module_instance.get_module_name()}")
        else:
            self.available = True
            logger.debug(f"{self.current_module} found among available modules")

    def load_module(self) -> PyModule:
        """
        Dynamically loads a Python module for processing based on the module instance's specifications.

        Returns:
            PyModule: An instance of the PyModule if successfully loaded, None otherwise.
        """

        modules_directory = OSIR_PATHS.PY_MODULES_DIR
        base_package = 'osir_lib.modules.'
        
        target_name = self._module_instance.alt_module or self._module_instance.module_name  # Try to load alt_module, fallback to module_name
        
        try:
            for _, name, is_pkg in pkgutil.walk_packages([modules_directory], base_package):
                if not is_pkg:
                    module = importlib.import_module(name)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, PyModule) and attr is not PyModule:
                            if name.split('.')[-1] == target_name:
                                return attr(self.case_path, self._module_instance)
        except ImportError as e:
            logger.debug(f"Failed to import {name}: {e}")
            return None

    def module_exists(self):
        """
        Checks if the Python module associated with the processor has been successfully loaded.

        Returns:
            bool: True if the module is loaded, False otherwise.
        """
        return True if self._py_module else False
    
    def run_module(self):
        """
        Executes the loaded Python module's processing function if the module is available.
        """
        if self.module_exists():
            logger.debug(f"Module found running {self._module_instance.module_name}()")
            self._py_module()
        else:
            logger.debug(f"Module not found {self._module_instance.module_name}")

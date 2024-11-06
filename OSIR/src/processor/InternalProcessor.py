import os
from ..utils import BaseModule
from ..log.logger_config import AppLogger 
from src.utils.PyModule import PyModule
import pkgutil
import importlib
import traceback

logger = AppLogger(__name__).get_logger()


class InternalProcessor:
    """
    Manages the execution of internal processing tasks within a Python environment, using predefined module instances.
    """
    def __init__(self, case_path: str, module_instance: BaseModule) -> None:
        """
        Initializes the InternalProcessor with a specific case path and module instance.

        Args:
            case_path (str): The base path where case files are stored and operations are performed.
            module_instance (BaseModule): The module instance defining the processing rules and configurations.
        """
        self._module_instance = module_instance
        self._module_instance.init_tool()  # Tool details initiated by agent (tools may bo presents only on agent)

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
        directory = os.path.dirname(__file__)  # Gets the directory of the current script
        relative_path = os.path.join(directory, '..')
        absolute_path = os.path.abspath(relative_path)  # Converts to absolute path
        modules_directory = os.path.join(absolute_path, 'modules')

        base_package = 'src.modules'
        
        try:
            for _, module_name, is_pkg in pkgutil.walk_packages([modules_directory], base_package + "."):
                if not is_pkg:
                    if module_name.endswith(self._module_instance.module_name):
                        module = importlib.import_module(module_name)
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if isinstance(attr, type) and issubclass(attr, PyModule) and attr is not PyModule:
                                return attr(self.case_path, self._module_instance)
        except Exception as e:
            logger.debug(f"Failed to import {self._module_instance.module_name}. Error {str(e)}")
            logger.debug(traceback.format_exc())
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

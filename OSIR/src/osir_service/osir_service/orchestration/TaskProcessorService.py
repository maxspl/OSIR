import importlib
import sys

from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()


class ExternalProcessor:
    """
    Handles the external processing of files based on the configuration of a specific module instance.
    """

    def __init__(self, case_path: str, module_instance: OsirModule, task_id=None, agent_name=None) -> None:
        """
        Initializes an ExternalProcessor instance with specified case path and module.

        Args:
            case_path (str): Path where case files are stored and operations are performed.
            module_instance (OsirModule): The module instance defining the processing rules.
        """
        self.agent_name = agent_name
        self.module_instance = module_instance
        self.task_id = task_id

    def run_module(self):
        """
        Executes the external tool associated with the module instance.
        """
        self.module_instance.tool.run(task_id=self.task_id, agent_id=self.agent_name)


class InternalProcessor:
    """
    Manages the execution of internal processing tasks within a Python environment, using predefined module instances.
    """

    def __init__(self, case_path: str, module_instance: OsirModule, task_id=None, agent_name=None) -> None:
        """
        Initializes the InternalProcessor with a specific case path and module instance.

        Args:
            case_path (str): The base path where case files are stored and operations are performed.
            module_instance (BaseModule): The module instance defining the processing rules and configurations.
        """
        self.task_id = task_id
        self.agent_name = agent_name
        self._module_instance = module_instance

        self.case_path = case_path  # Base directory for operations

        self.current_module = self._module_instance.get_module_name()
        self._py_module = self.load_module()

        if not self._py_module:
            self.available = False
            logger.error(f"selected module not found {self._module_instance.get_module_name()}")
        else:
            self.available = True
            logger.debug(f"{self.current_module} found among available modules")

    def load_module(self):
        """
        Dynamically loads a Python module for processing based on the module instance's specifications.

        Returns:
            PyModule: An instance of the PyModule if successfully loaded, None otherwise.
        """

        modules_directory = OSIR_PATHS.PY_MODULES_DIR
        # target_file = next(modules_directory.rglob(f"{self._module_instance.module_name}.py"), None)

        # 1. Determine which module name to look for (alt_module takes priority)
        target_name = (
            getattr(self._module_instance.configuration, "alt_module", None)
            or self._module_instance.module_name
        )        
        # 2. Search for the .py file
        target_file = next(modules_directory.rglob(f"{target_name}.py"), None)

        if not target_file:
            logger.error(f"File {target_name}.py not found in {modules_directory}")
            return None

        try:
            spec = importlib.util.spec_from_file_location(self._module_instance.module_name, target_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[self._module_instance.module_name] = module
                spec.loader.exec_module(module)

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if getattr(attr, "__osir_internal__", False):
                        return attr

        except Exception as e:
            print(f"Error while loading internal module - {target_file}: {e}")

        return None

    def module_exists(self):
        """
        Checks if the Python module associated with the processor has been successfully loaded.

        Returns:
            bool: True if the module is loaded, False otherwise.
        """
        return True if self._py_module else False

    def run_module(self) -> bool:
        """
        Executes the loaded Python module's processing function if the module is available.
        """
        if self.module_exists():
            logger.debug(f"Module found running {self._module_instance.module_name}()")

            # ADD PARAMETER TO SEND THEM TO THE INTERNAL FUNCTION
            return self._py_module(
                module=self._module_instance,
                case_path=self.case_path,
                task_id=self.task_id,
                agent_id=self.agent_name
            )
        else:
            logger.error(f"Module not found {self._module_instance.module_name}")
            return False

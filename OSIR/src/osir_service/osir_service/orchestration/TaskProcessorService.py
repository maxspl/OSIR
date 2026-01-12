import os
import pkgutil
import importlib
import sys
import traceback

from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger
       
logger = AppLogger(__name__).get_logger()

class ExternalProcessor:
    """
    Handles the external processing of files based on the configuration of a specific module instance.
    """
    def __init__(self, case_path: str, module_instance: OsirModule, task_id = None) -> None:
        """
        Initializes an ExternalProcessor instance with specified case path and module.

        Args:
            case_path (str): Path where case files are stored and operations are performed.
            module_instance (OsirModule): The module instance defining the processing rules.
        """
   
        # Declare module class from config string
        self.module_instance = module_instance
<<<<<<< HEAD
        self.task_id = task_id
=======
>>>>>>> f9f01e99634329d85149028840be42e94cd75666

    def run_module(self):
        """
        Executes the external tool associated with the module instance.
        """
<<<<<<< HEAD
        self.module_instance.tool.run(task_id=self.task_id)
=======
        self.module_instance.tool.run()
>>>>>>> f9f01e99634329d85149028840be42e94cd75666

class InternalProcessor:
    """
    Manages the execution of internal processing tasks within a Python environment, using predefined module instances.
    """
    def __init__(self, case_path: str, module_instance: OsirModule, task_id = None) -> None:
        """
        Initializes the InternalProcessor with a specific case path and module instance.

        Args:
            case_path (str): The base path where case files are stored and operations are performed.
            module_instance (BaseModule): The module instance defining the processing rules and configurations.
        """
        self.task_id = task_id
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
        target_file = next(modules_directory.rglob(f"{self._module_instance.module_name}.py"), None)

        if not target_file:
            print(f"Fichier {self._module_instance.module_name}.py non trouvé dans {modules_directory}")
            return None

        try:
            # Chargement dynamique du module Python
            spec = importlib.util.spec_from_file_location(self._module_instance.module_name, target_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                # Ajout au sys.modules pour éviter les problèmes d'imports relatifs
                sys.modules[self._module_instance.module_name] = module
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
                task_id=self.task_id
            )
        else:
            logger.error(f"Module not found {self._module_instance.module_name}")
            return False

from src.utils.PyModule import PyModule
from ..utils import BaseModule
from ..log.logger_config import AppLogger 
       
logger = AppLogger(__name__).get_logger()


class ExternalProcessor:
    """
    Handles the external processing of files based on the configuration of a specific module instance.
    """
    def __init__(self, case_path: str, module_instance: BaseModule) -> None:
        """
        Initializes an ExternalProcessor instance with specified case path and module.

        Args:
            case_path (str): Path where case files are stored and operations are performed.
            module_instance (BaseModule): The module instance defining the processing rules.
        """
   
        # Declare module class from config string
        self._module_instance = module_instance
        self._module_instance.init_tool()  # Tool details initiated by agent (tools may bo presents only on agent)
        self._py_module = PyModule(case_path, module_instance)

    def run_module(self):
        """
        Executes the external tool associated with the module instance.
        """
        self._py_module.run_ext_tool()

import re
import os
import copy
from datetime import datetime
from src.utils.UnixUtils import UnixUtils
from src.utils.BaseModule import BaseModule
from src.utils.PyModule import PyModule
from src.log.logger_config import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()

class InjectionModule(PyModule, UnixUtils):
    """
    PyModule to inject log into Splunk.
    """
    def __init__(self, case_path: str, module: BaseModule):
        """
        Initializes the Module.

        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (BaseModule): Instance of BaseModule containing configuration details for the extraction process.
        """
        PyModule.__init__(self, case_path, module)
        UnixUtils.__init__(self, case_path, module)

        self._dir_to_process = module.input.dir

    def __call__(self) -> bool:
        """
        Execute the internal processor of the module.

        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        try:
            logger.debug(f"Processing file {self._dir_to_process}")
            for dir_name in os.listdir(self._dir_to_process):
                if os.path.isdir(os.path.join(self._dir_to_process, dir_name)):
                    try:
                        module_to_process = BaseModule(dir_name)
                    except FileNotFoundError:
                        logger.warning(f"Skipping directory '{dir_name}' — no matching module found.")
                        continue  # Skip to next directory
                    if module_to_process:
                        logger.debug(f"Module found {dir_name}")
                        indexer_data = module_to_process.data.get('splunk',None)
                        if indexer_data: 
                            tool_ = copy.deepcopy(self.module.tool)
                            tool_.cmd = tool_.cmd.replace('{indexer_path}',os.path.join(self._dir_to_process, module_to_process._module_filepath))
                            tool_.cmd = tool_.cmd.replace('{input_dir}', os.path.join(self._dir_to_process, dir_name))
                            tool_.cmd = tool_.cmd.replace('{case_name}',os.path.basename(self._dir_to_process))
                            tool_.run_local()
                    else:
                        logger.warning(f"Module not found {dir_name}")

            logger.debug(f"{self.module.module_name} done")

        except Exception as exc:
            logger.error_handler(exc)
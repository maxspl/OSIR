import os
import re
import shutil
import random
import string
from ...utils.BaseModule import BaseModule 
from src.utils.PyModule import PyModule
from ...log.logger import AppLogger 

logger = AppLogger(__name__).get_logger()


class Linux_Processor(PyModule):
    """
    Extends PyModule to run parsing of Linux memory dump using volatility3.
    """
    def __init__(self, case_path: str, module: BaseModule):
        """
        Initializes the Linux_Processor with a specific case path and module configuration.

        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (BaseModule): Instance of BaseModule containing configuration details for the extraction process.
        """
        super().__init__(case_path, module)  # Init PyModule 

        self._case_path = case_path  # Base directory for operations
        self._file_to_process = module.input.file
        self._name_rex = self.module.input.name

    def __call__(self) -> bool:
        """
        Executes the Memory processing.

        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        logger.debug(f"Processing file {self.module.input.file}")

        # Run extraction
        self._run_volatility3_external_tool()
        logger.debug(f"{self.module.module_name} done")

    def _run_volatility3_external_tool(self):
        """
        Run volatility3 as configured in the yml configuration file.
        """
        self.run_ext_tool()

import os
import re
import shutil
import random
import string
from ...utils.BaseModule import BaseModule 
from src.utils.PyModule import PyModule
from ...log.logger import AppLogger 

logger = AppLogger(__name__).get_logger()


class Memory_Processor(PyModule):
    """
    Extends PyModule to run parsing of Windows memory dump using memprocfs.
    """
    def __init__(self, case_path: str, module: BaseModule):
        """
        Initializes the Memory_Processor with a specific case path and module configuration.

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
        self._move_memprocfs_script()
        logger.debug(f"{self.module.module_name} done")

    def _move_memprocfs_script(self):
        # Paths
        source_file = "/OSIR/OSIR/configs/dependencies/win_memprocfs_pythonexec_sample.py"
        destination_dir = "/tmp"
        output_dir = os.path.join("/OSIR/cases", self._case_path, self.module.module_name)

        # Generate a random filename
        random_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + ".py"
        self.pythonexec_path = os.path.join(destination_dir, random_filename)

        # Copy the file to /tmp with the new name
        shutil.copyfile(source_file, self.pythonexec_path)

        # Replace {output_dir} in the copied file
        with open(self.pythonexec_path, 'r') as file:
            file_contents = file.read()

        file_contents = file_contents.replace("{output_dir}", output_dir)

        with open(self.pythonexec_path, 'w') as file:
            file.write(file_contents)

        logger.debug(f"Memprocfs pythonexec file copied and modified: {self.pythonexec_path}")

        self._run_memprocfs_external_tool()
        
    def _run_memprocfs_external_tool(self):
        """
        Run memprocfs as configured in the yml configuration file.
        """
        self.module.optional['pythonexec_path'] = self.pythonexec_path
        self.run_ext_tool()

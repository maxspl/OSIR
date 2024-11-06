import os
import re
import shutil
from ...utils.BaseModule import BaseModule
from src.utils.PyModule import PyModule
from src.log.logger_config import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


class UAC_Extractor(PyModule):
    """
    PyModule to perform processing operations on UAC collect.
    """
    def __init__(self, case_path: str, module: BaseModule):
        """
        Initializes the Module.
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
        Execute the internal processor of the module
        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        logger.debug(f"Processing file {self.module.input.file}")

        pattern = re.compile(self._name_rex)

        match = pattern.match(os.path.basename(self._file_to_process))
        endpoint_name = match.groups()[0]
        archive_path = self._file_to_process
        archive_path = self._file_to_process
        endpoint_dir = os.path.join(self._case_path, self.module.get_module_name(), "Endpoint_" + endpoint_name)
        os.makedirs(endpoint_dir, exist_ok=True)
        moved_archive_path = os.path.join(endpoint_dir, os.path.basename(self._file_to_process))
        shutil.move(archive_path, moved_archive_path)
        extraction_dir = os.path.join(endpoint_dir, "extracted_files")
        os.makedirs(extraction_dir, exist_ok=True)
        try:
            self.module.input.file = moved_archive_path
            self.module.output.output_dir = extraction_dir
        except Exception as e:
            logger.error(f"Failed to extract {moved_archive_path}: {e}")

        self.run_ext_tool()
        # Process
        logger.debug(f"{self.module.module_name} done")

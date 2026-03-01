import os
import shutil
from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


@osir_internal_module
class UAC_Extractor():
    """
    PyModule to perform processing operations on UAC collect.
    """

    def __init__(self, case_path: str, module: OsirModule):
        """
        Initializes the Module.
        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (OsirModule): Instance of OsirModule containing configuration details for the extraction process.
        """
        self.module = module
        self._case_path = case_path  # Base directory for operations
        self._file_to_process = module.input.match
        self._name_rex = self.module.input.name

    def __call__(self) -> bool:
        """
        Execute the internal processor of the module
        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        logger.debug(f"Processing file {self.module.input.match}")
        archive_path = self._file_to_process
        endpoint_dir = os.path.join(self._case_path, self.module.get_module_name(), "Endpoint_" + self.module.endpoint_name)
        os.makedirs(endpoint_dir, exist_ok=True)

        self.module.tool.run()

        moved_archive_path = os.path.join(endpoint_dir, os.path.basename(self._file_to_process))
        shutil.move(archive_path, moved_archive_path)
        extraction_dir = os.path.join(endpoint_dir, "extracted_files")
        os.makedirs(extraction_dir, exist_ok=True)
        try:
            self.module.input.file = moved_archive_path
            self.module.output.output_dir = extraction_dir
        except Exception as e:
            logger.error(f"Failed to extract {moved_archive_path}: {e}")

        # Process
        logger.debug(f"{self.module.module_name} done")

import os
import re
import shutil
from ...utils.BaseModule import BaseModule 
from src.utils.PyModule import PyModule
from ...log.logger import AppLogger 

logger = AppLogger(__name__).get_logger()


class ORC_Extractor(PyModule):
    """
    Extends PyModule to perform extraction operations for DFIR ORC archives, maintaining directory structures and handling nested archives.
    """
    def __init__(self, case_path: str, module: BaseModule):
        """
        Initializes the ORC_Extractor with a specific case path and module configuration.

        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (BaseModule): Instance of BaseModule containing configuration details for the extraction process.
        """
        super().__init__(case_path, module)  # Init PyModule 

        self._cmd = self.module.tool.cmd  # Save cmd with place holders for further interations
        self._case_path = case_path  # Base directory for operations
        self._file_to_process = module.input.file
        self._name_rex = self.module.input.name

    def __call__(self) -> bool:
        """
        Executes the extraction process for the configured file, including moving and recursive extraction if necessary.

        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        logger.debug(f"Processing file {self.module.input.file}")

        # Run extraction
        self.move_and_extract_preserving_structure()
        logger.debug(f"{self.module.module_name} done")

    def extract_preserving_structure(self):
        """
        Extracts files and directories from the specified archive while preserving the original directory structure.
        """
        self.module.tool.cmd = self._cmd  # Restore cmd with place holders
        self.run_ext_tool()

    def move_and_extract_preserving_structure(self):
        """
        Moves the specified archive to a new location and extracts its contents, preserving the original directory structure.
        This method handles file matching, directory creation, and manages extraction for both top-level and nested archives.
        """
        pattern = re.compile(self._name_rex)  

        match = pattern.match(os.path.basename(self._file_to_process))
        endpoint_name, archive_name = match.groups()
        archive_path = self._file_to_process
        archive_path = self._file_to_process
        endpoint_dir = os.path.join(self._case_path, self.module.get_module_name(), "Endpoint_" + endpoint_name)
        os.makedirs(endpoint_dir, exist_ok=True)
        moved_archive_path = os.path.join(endpoint_dir, os.path.basename(self._file_to_process))
        shutil.move(archive_path, moved_archive_path)
        extraction_dir = os.path.join(endpoint_dir, "extracted_files", archive_name)
        os.makedirs(extraction_dir, exist_ok=True)
        try:
            self.module.input.file = moved_archive_path
            self.module.output.output_dir = extraction_dir
            self.extract_preserving_structure()
        except Exception as e:
            logger.error(f"Failed to extract {moved_archive_path}: {e}")

        # Post extraction handling for nested archives
        for root, dirs, files in os.walk(extraction_dir):
            for file in files:
                if file.endswith('.7z'):
                    input_path = os.path.join(root, file)
                    nested_archive_name = os.path.basename(os.path.splitext(input_path)[0])
                    try:
                        nested_extraction_dir = os.path.join(root, nested_archive_name)
                        os.makedirs(nested_extraction_dir, exist_ok=True)
                        self.module.input.file = input_path
                        self.module.output.output_dir = nested_extraction_dir
                        self.extract_preserving_structure()
                        os.remove(input_path)  # Remove the archive after extraction
                    except Exception as e:
                        logger.error(f"Failed to extract nested archive {input_path}: {e}")

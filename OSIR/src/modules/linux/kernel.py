import re
from src.utils.UnixUtils import UnixUtils
from ...utils.BaseModule import BaseModule
from src.utils.PyModule import PyModule
from src.log.logger_config import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()

class KernelModule(PyModule, UnixUtils):
    """
    PyModule to perform processing operations on Kernel logs.
    """
    def __init__(self, case_path: str, module: BaseModule):
        """
        Initializes the Module.

        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (BaseModule): Instance of BaseModule containing configuration details for the extraction process.
        """
        PyModule.__init__(self, case_path, module)  # Init PyModule
        UnixUtils.__init__(self, case_path, module)
        self._file_to_process = module.input.file

        # Parsing structure with regex and safe_search
        self.structure = [
            ("_time", lambda log: self.safe_search(r"^(\w+\s+\d{1,2}\s\S+)", log)),
            ("_host", lambda log: self.safe_search(r"^\w+\s+\d{1,2}\s\S+\s+(\S+)\s", log)),
            ("_type", lambda log: self.safe_search(r"^\w+\s+\d{1,2}\s\S+\s+\S+\s+(\S+)", log).replace(':', '')),
            ("_offset", lambda log: self.safe_search(r"\[(.*?)\]", log)),
            ("_sector", lambda log: self.safe_search(r"\S+:+\s", log)),
            ("_raw", lambda log: log)
        ]

    def __call__(self) -> bool:
        """
        Execute the internal processor of the module.

        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        try:
            writer_queue = self.start_writer_thread()
            logger.debug(f"Processing file {self._file_to_process}")

            for log in self.get_log():
                writer_queue.put(self.parse(log))

            writer_queue.put(None)
            logger.debug(f"{self.module.module_name} done")
            return True
        except Exception as exc:
            logger.error_handler(exc)
            return False

    def parse(self, log):
        """
        Parse a single log according to the structure defined in the init.
        
        Args:
            log (str): The log string to parse.
        
        Returns:
            dict: Parsed log data.
        """
        return {field: parser(log) for field, parser in self.structure}
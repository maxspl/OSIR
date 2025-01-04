import re
from src.utils.UnixUtils import UnixUtils
from ...utils.BaseModule import BaseModule
from src.utils.PyModule import PyModule
from src.log.logger_config import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


class YumModule(PyModule, UnixUtils):
    """
    PyModule to perform processing operations on Yum logs.
    """
    def __init__(self, case_path: str, module: BaseModule):
        """
        Initializes the Module.

        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (BaseModule): Instance of BaseModule containing configuration details for the extraction process.
        """
        PyModule.__init__(self, case_path, module)  # Init PyModule
        UnixUtils.__init__(self, case_path, module)  # Init UnixUtils
        self._file_to_process = module.input.file
        self._name_rex = self.module.input.name

        # PARSING OUTPUT STRUCTURE
        self.structure = {
            "_time": lambda log: self.get_date(
                log, r'[A-Z][a-z]{2} \d{1,2} \d{2}:\d{2}:\d{2}', '%b %d %H:%M:%S'
            ),
            "package_name": lambda log: re.search(r"(Installed|Updated):\s(.*)$", log).group(2),
            "event_type": lambda log: "package_install" if "Installed" in log else "package_update" if "Updated" in log else None
        }

        self._format_output_file()
        
    def __call__(self) -> bool:
        """
        Execute the internal processor of the module.

        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        try:
            writer_queue = self.start_writer_thread()
            logger.debug(f"Processing file {self.module.input.file}")

            for log in self.get_log():
                writer_queue.put(self.parse(log))

            writer_queue.put(None)
            logger.debug(f"{self.module.module_name} done")
        except Exception as exc:
            logger.error_handler(exc)

    def parse(self, log):
        """
        Parse a single log line using the structure defined in the init.
        
        Args:
            log (str): The log line to parse.
        
        Returns:
            dict: Parsed log data.
        """
        return {field: parser(log) for field, parser in self.structure.items() | {"_raw": log}}

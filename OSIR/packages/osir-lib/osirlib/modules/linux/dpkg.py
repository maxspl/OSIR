import re
import datetime
from src.utils.UnixUtils import UnixUtils
from ...utils.BaseModule import BaseModule
from src.utils.PyModule import PyModule
from src.log.logger_config import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


class DpkgModule(PyModule, UnixUtils):
    """
    PyModule to perform processing operations on Dpkg logs.
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

        self._file_to_process = module.input.file

        # Structure using regex and lambdas with safe_search for parsing log entries
        self.structure = [
            ("_time", lambda log: self.safe_search(r"^(\d+-\d+-\d+\s\d+:\d+:\d+)\s", log)),
            ("package_name", lambda log: self.safe_search(r"(?:installed|half-configured|upgrade)\s(.*)$", log)),
            ("event_type", lambda log: self.get_event_type(log)),
            ("_raw", lambda log: log)
        ]

        self._format_output_file()
        
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
                parsed_log = self.parse(log)
                if parsed_log.get("event_type") != "unknown":
                    writer_queue.put(parsed_log)

            writer_queue.put(None)
            logger.debug(f"{self.module.module_name} done")
            return True
        except Exception as exc:
            logger.error_handler(exc)
            return False

    def parse(self, log):
        """
        Parse a single log entry based on the structure defined.

        Args:
            log (str): The log entry to parse.

        Returns:
            dict: Parsed log data.
        """
        return {field: parser(log) for field, parser in self.structure}

    def get_event_type(self, log):
        """
        Determines the event type from the log.

        Args:
            log (str): The log entry to evaluate.

        Returns:
            str: Event type based on log content (package_install, package_configure, package_upgrade, unknown).
        """
        if "status half-installed" in log or "status installed" in log:
            return "package_install"
        elif "status half-configured" in log:
            return "package_configure"
        elif "upgrade" in log:
            return "package_upgrade"
        return "unknown"
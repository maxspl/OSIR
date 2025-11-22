import re
from src.utils.UnixUtils import UnixUtils
from ...utils.BaseModule import BaseModule
from src.utils.PyModule import PyModule
from src.log.logger_config import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


class CronModule(PyModule, UnixUtils):
    """
    PyModule to perform processing operations on Cron logs.
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
            ("_time", lambda log: self.safe_search(r"^(\w+\s+\d{1,2}\s\S+)", log)),  # Example: Jun 5 11:01:01
            ("hostname", lambda log: self.safe_search(r"^\w+\s+\d{1,2}\s\S+\s+(\S+)", log)),
            ("app", lambda log: self.safe_search(r"^\w+\s+\d{1,2}\s\S+\s+\S+\s+(\S+)", log)),
            ("_raw", lambda log: log),
            ("cron_name", lambda log: self.safe_search(r"(starting|finished)\s(.*)", log)),
            ("event_type", lambda log: self.get_event_type(log)),
            ("user", lambda log: self.safe_search(r":\s\(([^\)]*)\)", log)),
            ("command_line", lambda log: self.safe_search(r"CMD\s\((.*)\)", log)),
            ("job_name", lambda log: self.safe_search(r"Job\s\`([^\']+)'", log)),
            ("service_related", lambda log: self.safe_search(r"LIST\s\(([^\)]*)\)", log))
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
            str: Event type based on log content (starting_cron, finished_cron, cron_process_creation, etc.).
        """
        if "starting" in log:
            return "starting_cron"
        elif "finished" in log:
            return "finished_cron"
        elif "CMD" in log:
            return "cron_process_creation"
        elif "Job" in log:
            return "job_started" if "started" in log else "job_terminated"
        elif "LIST" in log:
            return "list_cron"
        return "unknown"

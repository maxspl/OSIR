import re
from src.utils.UnixUtils import UnixUtils
from ...utils.BaseModule import BaseModule
from src.utils.PyModule import PyModule
from src.log.logger_config import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


class BodyfileModule(PyModule, UnixUtils):
    """
    PyModule to perform processing operations on Bodyfile.
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

        # Structure using regex and lambdas for parsing log entries
        self.regex_pattern = (
            r'^(?P<na>\d+)\|(?P<filename>[^|]+)\|(?P<inode>\d+)\|(?P<mode_as_string>[^|]+)\|'
            r'(?P<uid>\d+)\|(?P<gid>\d+)\|(?P<size>\d+)\|(?P<atime>\d+)\|(?P<mtime>\d+)\|'
            r'(?P<ctime>\d+)\|(?P<btime>\d+)?$'
        )

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
                if log.strip():  # Ensure log is not empty
                    parsed_log = self.parse(log)
                    if parsed_log:
                        writer_queue.put(parsed_log)

            writer_queue.put(None)
            logger.debug(f"{self.module.module_name} done")
            return True
        except Exception as exc:
            logger.error_handler(exc)
            return False

    def parse(self, log):
        """
        Parse a single log entry based on the regex pattern.

        Args:
            log (str): The log entry to parse.

        Returns:
            dict: Parsed log data or None if the log doesn't match the pattern.
        """
        match = re.match(self.regex_pattern, log)
        if match:
            parsed_log = match.groupdict()
            parsed_log['_raw'] = log
            return parsed_log
        return None

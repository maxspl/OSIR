from src.utils.UnixUtils import UnixUtils
from ...utils.BaseModule import BaseModule
from src.utils.PyModule import PyModule
from src.log.logger_config import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


class PostgresqlModule(PyModule, UnixUtils):
    """
    PyModule to perform processing operations on postgresql logs.
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
        self._case_path = case_path  # Base directory for operations
        self._file_to_process = module.input.file
        self._name_rex = self.module.input.name

        # PARSING OUTPUT STRUCTURE
        self.structure = {
            "_time": lambda log: self.get_date(
                log, r'(19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]) \d{2}:\d{2}:\d{2}\.\d{3}', '%Y-%m-%d %H:%M:%S.%f'
            ),
            "severity": lambda log: self.get_severity(log)
        }

    def __call__(self) -> bool:
        """
        Execute the internal processor of the module

        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        try:
            logger.debug(f"""Processing Started: \n
                    File Input: {self.module.input.file} \n""")
            
            writer_queue = self.start_writer_thread()

            for line in self.get_log():
                writer_queue.put(self.parse(line))

            writer_queue.put(None)

            logger.debug(f"""Processing Done: \n
                    File Input: {self.module.input.file} \n""")

        except Exception as exc:
            logger.error_handler(exc)

    def parse(self, log: str) -> dict:
        """
        Parse a single log line using the structure defined in the init.
        
        Args:
            log (str): The log line to parse.
        
        Returns:
            dict: Parsed log data.
        """
        parsed_log = {field: parser(log) for field, parser in self.structure.items()}
        parsed_log["_raw"] = log

        return parsed_log
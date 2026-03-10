from osir_lib.core.LogUtils import LogUtils
from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


@osir_internal_module
class MailModule(LogUtils):
    """
    PyModule to perform processing operations on mail logs.
    """

    def __init__(self, module: OsirModule):
        """
        Initializes the Module.

        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (OsirModule): Instance of OsirModule containing configuration details for the extraction process.
        """
        self.module = module
        LogUtils.__init__(self, ctx=module)
        self._file_to_process = module.input.match
        self._name_rex = self.module.input.name

        self.structure = {
            "_time": lambda log: self.get_date(
                log, r'^(\w+\s+\d{1,2}\s\S+)', '%Y %b %d %H:%M:%S'
            ),
            "severity": lambda log: self.get_severity(log),
            "src_mail": lambda log: self.safe_search(r'from=\<([^\>]*)\>', log),
            "dest_mail": lambda log: self.safe_search(r'to=\<([^\>]*)\>', log),
            "subject": lambda log: self.safe_search(r'(?<=Subject: ).*?(?=\sfrom)', log),
            "message_id": lambda log: self.safe_search(r'^\S+\s+\d+\s\d+:\d+:\d+\s\S+\s\S+\s([A-Z0-9]+):', log)
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
            return False
        return True

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

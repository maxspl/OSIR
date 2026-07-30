import re
from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.LogUtils import LogUtils
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


@osir_internal_module
class YumModule(LogUtils):
    """
    PyModule to perform processing operations on Yum logs.
    """

    def __init__(self, case_path: str, module: OsirModule):
        """
        Initializes the Module.

        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (OsirModule): Instance of OsirModule containing configuration details for the extraction process.
        """
        self.module = module
        LogUtils.__init__(self, ctx=module)
        self._file_to_process = module.input.file
        self._name_rex = self.module.input.name

        # PARSING OUTPUT STRUCTURE
        self.structure = {
            "_time": lambda log: self.get_date(
                log, r'[A-Z][a-z]{2} \d{1,2} \d{2}:\d{2}:\d{2}', '%b %d %H:%M:%S'
            ),
            "package_name": lambda log: self.safe_search(r"(?:Installed|Updated):\s(.*)$", log),
            "event_type": lambda log: "package_install" if "Installed" in log else "package_update" if "Updated" in log else None
        }

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
        except Exception as exc:
            logger.error_handler(exc)
            return False
        return True

    def parse(self, log):
        """
        Parse a single log line using the structure defined in the init.

        Args:
            log (str): The log line to parse.

        Returns:
            dict: Parsed log data.
        """
        # `self.structure.items() | {"_raw": log}` unioned a dict_items view with
        # a dict: iterating a dict yields its keys, so the set held both 2-tuples
        # and the bare string "_raw", which then failed to unpack into
        # (field, parser). Every line raised, so the module never emitted anything.
        parsed_log = {field: parser(log) for field, parser in self.structure.items()}
        parsed_log["_raw"] = log

        return parsed_log

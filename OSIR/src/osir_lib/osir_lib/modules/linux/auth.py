import re
from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.LogUtils import LogUtils
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


@osir_internal_module
class AuthModule(LogUtils):
    """
    PyModule to perform processing operations on Boot logs.
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
        self._file_to_process = module.input.match

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
                to_return = {'_raw': log}

                match = re.match('^(?P<date>\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+(?P<process>[-_\w]+)\[?(?P<pid>\d+)?\]?:\s(?P<message>.+)$', log)

                if match:
                    to_return.update(match.groupdict())

                writer_queue.put(to_return)

            writer_queue.put(None)
            logger.debug(f"{self.module.module_name} done")

        except Exception as exc:
            logger.error_handler(exc)
            return False
        return True

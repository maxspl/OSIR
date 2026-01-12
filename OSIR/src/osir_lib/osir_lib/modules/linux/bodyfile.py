import re
from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.LogUtils import LogUtils
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger(__name__).get_logger()

<<<<<<< HEAD
@osir_internal_module(trace=False)
=======
@osir_internal_module(trace=True)
>>>>>>> f9f01e99634329d85149028840be42e94cd75666
class BodyfileModule(LogUtils):
    """
    PyModule to perform processing operations on Bodyfile.
    """
    def __init__(self, module: OsirModule, task_id: str):
        """
        Initializes the Module.

        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (OsirModule): Instance of OsirModule containing configuration details for the extraction process.
        """
        self.ctx = module

        self.task_id = task_id
        LogUtils.__init__(self,ctx=module)

        self._file_to_process = module.input.match

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
            logger.info(f"""[AGENT][{self.task_id}] Processing started : \n
                            - Module : {self.ctx.module_name} \n
                            - Input  : {self._file_to_process} \n """)
            
            writer_queue = self.start_writer_thread()
            logger.debug(f"TASK:{self.task_id} Processing file {self._file_to_process}")

            for log in self.get_log():
                if log.strip():  # Ensure log is not empty
                    parsed_log = self.parse(log)
                    if parsed_log:
                        writer_queue.put(parsed_log)

            writer_queue.put(None)
            logger.debug(f"{self.ctx.module_name} done")
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

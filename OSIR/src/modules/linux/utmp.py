import ipaddress
import struct
import time
from src.utils.UnixUtils import UnixUtils
from ...utils.BaseModule import BaseModule
from src.utils.PyModule import PyModule
from src.log.logger_config import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()

class UtmpModule(PyModule, UnixUtils):
    """
    PyModule to perform processing operations on binary UTMP files.
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

        # Status mapping for ut_type
        self.STATUS = {
            0: 'EMPTY',
            1: 'RUN_LVL',
            2: 'BOOT_TIME',
            3: 'NEW_TIME',
            4: 'OLD_TIME',
            5: 'INIT_PROCESS',
            6: 'LOGIN_PROCESS',
            7: 'USER_PROCESS',
            8: 'DEAD_PROCESS',
            9: 'ACCOUNTING'
        }

        # Parsing structure
        self.structure = [
            ("ut_type", lambda log: self.STATUS.get(struct.unpack("<L", log[:4])[0], 'UNKNOWN')),
            ("ut_pid", lambda log: struct.unpack("<L", log[4:8])[0]),
            ("ut_line", lambda log: log[8:40].decode("utf-8", "replace").split('\0', 1)[0]),
            ("ut_id", lambda log: log[40:44].decode("utf-8", "replace").split('\0', 1)[0]),
            ("ut_user", lambda log: log[44:76].decode("utf-8", "replace").split('\0', 1)[0].replace("\n", "/n")),
            ("ut_host", lambda log: log[76:332].decode("utf-8", "replace").split('\0', 1)[0]),
            ("e_termination", lambda log: struct.unpack("<H", log[332:334])[0]),
            ("e_exit", lambda log: struct.unpack("<H", log[334:336])[0]),
            ("ut_session", lambda log: struct.unpack("<L", log[336:340])[0]),
            ("tv_sec", lambda log: time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(struct.unpack("<L", log[340:344])[0]))),
            ("tv_usec", lambda log: struct.unpack("<L", log[344:348])[0]),
            ("IPv4", lambda log: ipaddress.IPv4Address(struct.unpack(">L", log[348:352])[0]).__str__())
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
            logger.debug(f"Processing file {self.module.input.file}")

            with open(self._file_to_process, "rb") as utmp_file:
                while chunk := utmp_file.read(384):  # Read 384 bytes per record
                    writer_queue.put(self.parse(chunk))

            writer_queue.put(None)
            logger.debug(f"{self.module.module_name} done")
        except Exception as exc:
            logger.error_handler(exc)

    def parse(self, log_chunk):
        """
        Parse a single log chunk according to the structure defined in the init.
        
        Args:
            log_chunk (bytes): The binary data chunk to parse.
        
        Returns:
            dict: Parsed log data.
        """
        return {field: parser(log_chunk) for field, parser in self.structure}

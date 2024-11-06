import struct
import time
from src.utils.UnixUtils import UnixUtils
from ...utils.BaseModule import BaseModule
from src.utils.PyModule import PyModule
from src.log.logger_config import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()

class LastlogModule(PyModule, UnixUtils):
    """
    PyModule to perform processing operations on Lastlog files.
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

        # Parsing structure for actual and legacy formats
        self.structures = {
            "actual": [
                ("_time", lambda log: time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(struct.unpack("<L", log[:4])[0]))),
                ("line", lambda log: log[4:36].rstrip(b"\x00").decode("utf-8", "replace")),
                ("host", lambda log: log[36:292].rstrip(b"\x00").decode("utf-8", "replace")),
            ],
            "legacy": [
                ("_time", lambda log: time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(struct.unpack("<L", log[:4])[0]))),
                ("line", lambda log: log[4:12].rstrip(b"\x00").decode("utf-8", "replace")),
                ("host", lambda log: log[12:28].rstrip(b"\x00").decode("utf-8", "replace")),
            ]
        }

        # Structures sizes
        self.struct_size = {
            "actual": 292,
            "legacy": 28
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

            with open(self._file_to_process, "rb") as lastlog_file:
                size = len(lastlog_file.read())
                offset = 0
                uid = 0
                while offset < size:
                    lastlog_file.seek(offset)
                    log_entry = lastlog_file.read(self.struct_size["actual"])

                    try:
                        parsed_log = self.parse(log_entry, "actual")
                    except struct.error:
                        logger.warning("Actual format failed, trying legacy format")
                        log_entry = lastlog_file.read(self.struct_size["legacy"])
                        parsed_log = self.parse(log_entry, "legacy")

                    if parsed_log["_time"] != "1970/01/01 01:00:00": 
                        parsed_log["uid"] = uid
                        writer_queue.put(parsed_log)

                    uid += 1
                    offset += self.struct_size["actual"]

            writer_queue.put(None)
            logger.debug(f"{self.module.module_name} done")
            return True
        except Exception as exc:
            logger.error_handler(exc)
            return False

    def parse(self, log_chunk, format_type):
        """
        Parse a single log chunk according to the given format.

        Args:
            log_chunk (bytes): The binary data chunk to parse.
            format_type (str): The format type, either 'actual' or 'legacy'.

        Returns:
            dict: Parsed log data.
        """
        return {field: parser(log_chunk) for field, parser in self.structures[format_type]}

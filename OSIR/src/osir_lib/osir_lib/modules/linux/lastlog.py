import struct
from datetime import datetime, timezone
from pathlib import Path

from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.LogUtils import LogUtils
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()

# struct lastlog { int32 ll_time; char ll_line[32]; char ll_host[256]; }
_RECORD_SIZE = 292
_LINE_SLICE = slice(4, 36)
_HOST_SLICE = slice(36, 292)


@osir_internal_module
class LastlogModule(LogUtils):
    """
    PyModule to perform processing operations on Lastlog files.

    /var/log/lastlog is a sparse array indexed by UID: record N describes UID N,
    and an all-zero record just means that UID never logged in. Those are skipped
    rather than emitted.
    """

    def __init__(self, module: OsirModule):
        """
        Initializes the Module.

        Args:
            module (OsirModule): Instance of OsirModule containing configuration details for the extraction process.
        """
        self.module = module
        LogUtils.__init__(self, ctx=module)
        self._file_to_process = module.input.match
        self._users = self._load_users()

    def _load_users(self) -> dict:
        """
        Maps UIDs to user names using the /etc/passwd of the same collection.

        lastlog only stores UIDs, which are useless on their own during triage.
        The passwd file sits next to the log inside the collected filesystem
        root (…/[root]/var/log/lastlog -> …/[root]/etc/passwd).

        Returns:
            dict: UID to user name mapping, empty if passwd is unavailable.
        """
        try:
            passwd = Path(self._file_to_process).parent.parent.parent / "etc" / "passwd"
            if not passwd.is_file():
                return {}

            users = {}
            with open(passwd, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    fields = line.split(":")
                    if len(fields) < 3:
                        continue
                    try:
                        users[int(fields[2])] = fields[0]
                    except ValueError:
                        continue
            return users
        except OSError as exc:
            logger.debug(f"Could not read passwd for lastlog enrichment: {exc}")
            return {}

    def __call__(self) -> bool:
        """
        Execute the internal processor of the module.

        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        try:
            writer_queue = self.start_writer_thread()
            logger.debug(f"Processing file {self._file_to_process}")

            count = 0
            with open(self._file_to_process, "rb") as lastlog_file:
                for uid in range(0, 2 ** 32):
                    record = lastlog_file.read(_RECORD_SIZE)
                    if len(record) < _RECORD_SIZE:
                        if record:
                            logger.warning(
                                f"Trailing {len(record)} bytes in {self._file_to_process}, "
                                f"file is truncated"
                            )
                        break

                    parsed_log = self.parse(record, uid)
                    if parsed_log:
                        writer_queue.put(parsed_log)
                        count += 1

            writer_queue.put(None)
            logger.debug(f"{self.module.module_name} done: {count} logins")
        except Exception as exc:
            logger.error_handler(exc)
            return False
        return True

    def parse(self, record: bytes, uid: int) -> dict:
        """
        Parse a single lastlog record.

        Args:
            record (bytes): The 292-byte record to parse.
            uid (int): The UID this record position corresponds to.

        Returns:
            dict: Parsed log data, or None when the UID never logged in.
        """
        timestamp = struct.unpack("<I", record[:4])[0]
        if timestamp == 0:
            return None

        return {
            "_time": datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat(),
            "epoch": timestamp,
            "uid": uid,
            "user": self._users.get(uid),
            "line": record[_LINE_SLICE].split(b"\x00", 1)[0].decode("utf-8", "replace"),
            "host": record[_HOST_SLICE].split(b"\x00", 1)[0].decode("utf-8", "replace"),
        }

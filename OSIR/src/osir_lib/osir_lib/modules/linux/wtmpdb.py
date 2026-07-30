import sqlite3
from datetime import datetime, timedelta, timezone

from osir_lib.core.LogUtils import LogUtils
from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# wtmpdb reuses the utmp ut_type numbering but only ever writes these three.
# See wtmpdb(8) / <utmp.h>.
_TYPES = {
    1: 'BOOT_TIME',
    2: 'RUNLEVEL',
    3: 'USER_PROCESS',
}


@osir_internal_module
class WtmpdbModule(LogUtils):
    """
    PyModule parsing /var/log/wtmp.db, the SQLite login database introduced by
    wtmpdb (Debian 13+, openSUSE, Fedora 42+).

    It replaces the binary utmp/wtmp/btmp files on those distributions, so a
    classic utmp parser reads it as garbage. One row is one *session*: it holds
    both the login and the logout time, whereas legacy wtmp needs two records.
    """

    def __init__(self, module: OsirModule):
        """
        Initializes the Module.

        Args:
            module (OsirModule): Instance of OsirModule containing configuration details.
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
        writer_queue = None
        try:
            logger.debug(f"Processing file {self._file_to_process}")

            # Open read-only so a live/locked database is never modified.
            uri = f"file:{self._file_to_process}?mode=ro"
            with sqlite3.connect(uri, uri=True) as connection:
                connection.row_factory = sqlite3.Row

                if not self._has_wtmp_table(connection):
                    logger.warning(
                        f"{self._file_to_process} is not a wtmpdb database "
                        f"(no 'wtmp' table), skipping"
                    )
                    return True

                writer_queue = self.start_writer_thread()
                count = 0
                for row in connection.execute(
                    "SELECT ID, Type, User, Login, Logout, TTY, RemoteHost, Service FROM wtmp"
                ):
                    writer_queue.put(self.parse(row))
                    count += 1

            writer_queue.put(None)
            writer_queue = None
            logger.debug(f"{self.module.module_name} done: {count} sessions")

        except sqlite3.DatabaseError as exc:
            # A truncated or non-SQLite file is a data problem, not a code one.
            logger.error(f"Failed to read wtmpdb '{self._file_to_process}': {exc}")
            if writer_queue is not None:
                writer_queue.put(None)
            return False
        except Exception as exc:
            logger.error_handler(exc)
            if writer_queue is not None:
                writer_queue.put(None)
            return False
        return True

    @staticmethod
    def _has_wtmp_table(connection) -> bool:
        """
        Checks the database actually holds a wtmpdb 'wtmp' table.

        Args:
            connection (sqlite3.Connection): The open database connection.

        Returns:
            bool: True if the 'wtmp' table exists.
        """
        row = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='wtmp'"
        ).fetchone()
        return row is not None

    @staticmethod
    def _to_iso(usecs) -> str:
        """
        Converts a wtmpdb timestamp to an ISO 8601 UTC string.

        wtmpdb stores microseconds since the Unix epoch, and leaves Logout NULL
        while the session is still open.

        Args:
            usecs (int | None): Microseconds since the Unix epoch.

        Returns:
            str: ISO 8601 UTC timestamp, or None if unset/unparseable.
        """
        if usecs is None:
            return None
        try:
            return (_EPOCH + timedelta(microseconds=int(usecs))).isoformat()
        except (ValueError, OverflowError, OSError):
            return None

    def parse(self, row) -> dict:
        """
        Parse a single wtmpdb row.

        Args:
            row (sqlite3.Row): The database row to parse.

        Returns:
            dict: Parsed session data.
        """
        login = self._to_iso(row["Login"])
        logout = self._to_iso(row["Logout"])

        return {
            "_time": login,
            "id": row["ID"],
            "type": _TYPES.get(row["Type"], f"UNKNOWN({row['Type']})"),
            "type_id": row["Type"],
            "user": row["User"],
            "login_time": login,
            "logout_time": logout,
            "session_open": logout is None,
            "tty": row["TTY"],
            "remote_host": row["RemoteHost"],
            "service": row["Service"],
        }

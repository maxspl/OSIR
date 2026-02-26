import io
from sqlite3 import OperationalError
from typing import Union, List, Tuple
import uuid
from osir_lib.core.FileManager import FileManager
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()


class OsirDbSnapshot:
    def __init__(self, db_osir):
        self.db = db_osir

    def create_table(self):
        query = """
            CREATE TABLE IF NOT EXISTS case_snapshot (
                case_uuid TEXT NOT NULL,
                case_path TEXT NOT NULL,
                path TEXT NOT NULL,
                entry_type TEXT NOT NULL,
                PRIMARY KEY (case_uuid, path)
            )
            """
        try:
            self.db.execute_query(query)
            #logger.debug("Table `case_snapshot` ensured.")
        except Exception as e:
            logger.error(f"Error creating `case_snapshot` table: {str(e)}")

    def get_stored_case_snapshot(self, case_path: str) -> List[Tuple[str, str]]:
        """
            Retrieves all file/directory entries stored for a specific case path from the snapshot.

            Args:
                case_path (str): The path of the case to look up.

            Returns:
                List[Tuple[str, str]]: A list of tuples containing (path, entry_type).
        """
        case_path = str(case_path)
        query = """
            SELECT path, entry_type
            FROM case_snapshot
            WHERE case_path = %s
        """
        try:
            rows = self.db.execute_query(query, (case_path,), fetch="fetchall")
            logger.debug(f"Retrieved {len(rows)} entries for case_path: {case_path}")
            return [(row[0], row[1]) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching entries for case_path {case_path}: {str(e)}")
            return []

    def store_case_snapshot(self, case_uuid: str, case_path: str, entries_list: List[Tuple[str, str]]):
        """
            Performs a bulk update of the case snapshot. Clears existing records for the case 
            and uses a fast COPY command to insert new unique entries.

            Args:
                case_uuid (str): The unique identifier of the case.
                case_path (str): The root path of the case.
                entries_list (List[Tuple[str, str]]): A list of (path, entry_type) to be stored.

            Note:
                This method filters out duplicate paths and paths containing backslashes 
                before performing the bulk insert via a buffer.

            Raises:
                OperationalError: If the database connection cannot be established.
                Exception: For any errors during the bulk copy process.
        """
        try:
            case_path = str(case_path)
            case_uuid = str(case_uuid)

            self.db.execute_query("DELETE FROM case_snapshot WHERE case_uuid = %s", (case_uuid,))

            seen_paths = set()
            unique_entries = []

            for path, entry_type in entries_list:
                path = str(path)
                if '\\' in path:
                    continue
                if path not in seen_paths:
                    seen_paths.add(path)
                    unique_entries.append((path, entry_type))

            output = io.StringIO()
            for path, entry_type in unique_entries:
                output.write(f"{case_uuid}\t{case_path}\t{path}\t{entry_type}\n")
            output.seek(0)

            conn = self.db._ensure_connection()
            if not conn:
                raise OperationalError("Could not establish a database connection.")

            with conn.cursor() as cur:
                cur.copy_from(
                    file=output,
                    table='case_snapshot',
                    columns=('case_uuid', 'case_path', 'path', 'entry_type'),
                    null=''
                )
            conn.commit()

        except Exception as e:
            logger.error(f"Bulk insert error for case_uuid {case_uuid}: {str(e)}")

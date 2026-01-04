import datetime
import io
from typing import List, Tuple
from psycopg2 import sql
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

class UtilsManager:
    def __init__(self, db_osir):
        self.db = db_osir

    def store_data(self, case_path: str, module: OsirModule, status: str, case_uuid: str):
        case_path = str(case_path)
        input_file = module.input.match
        input_dir = module.input.match
        output_file = module.output.output_file
        output_dir = module.output.output_dir
        output_prefix = module.output.output_prefix

        self.db.cur.execute(f"""
            INSERT INTO {module.module_name} (
                case_uuid,
                case_path,
                agent,
                input_file,
                input_dir,
                output_file,
                output_dir,
                output_prefix,
                processing_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(case_uuid),
            case_path,
            self.db.host_hostname,
            input_file,
            input_dir,
            output_file,
            output_dir,
            output_prefix,
            status
        ))
        self.db.conn.commit()

    def update_record(self, module: OsirModule, status: str, case_uuid: str):
        try:
            input_file = module.input.match
            input_dir = module.input.match
            output_file = module.output.output_file
            output_dir = module.output.output_dir
            output_prefix = module.output.output_prefix

            update_data = {
                "agent": self.db.host_hostname,
                "input_file": input_file,
                "input_dir": input_dir,
                "output_file": output_file,
                "output_dir": output_dir,
                "output_prefix": output_prefix,
                "processing_status": status
            }

            set_clause = ', '.join([f"{col} = %s" for col in update_data.keys()])
            values = list(update_data.values())

            update_query = f"""
                UPDATE {module.module_name}
                SET {set_clause}
                WHERE case_uuid = %s
                    AND ((input_file != '' AND input_file = %s)
                    OR (input_dir != '' AND input_dir = %s))
            """

            self.db.cur.execute(update_query, values + [case_uuid, input_file, input_dir])
            self.db.conn.commit()
            logger.debug(f"Database updated {self.db.cur.rowcount} record(s).")
        except Exception as error:
            logger.error(f"Error updating record: {error}")

    def store_master_status(self, case_path: str, status: str, case_uuid: str, modules_selected: str):
        case_path = str(case_path)
        current_timestamp = datetime.datetime.now()
        try:
            self.db.cur.execute("""
                SELECT 1 FROM master_status WHERE case_path = %s
            """, (case_path,))
            exists = self.db.cur.fetchone()

            if exists:
                self.db.cur.execute("""
                    UPDATE master_status
                    SET status = %s, case_uuid = %s, timestamp = %s, modules_selected = %s
                    WHERE case_path = %s
                """, (status, case_uuid, current_timestamp, modules_selected, case_path))
            else:
                self.db.cur.execute("""
                    INSERT INTO master_status (case_path, status, case_uuid, modules_selected)
                    VALUES (%s, %s, %s, %s)
                """, (case_path, status, case_uuid, modules_selected))
            self.db.conn.commit()
            action = "Updated" if exists else "Inserted"
            logger.debug(f"{action} master_status record for case_path: {case_path}")
        except Exception as error:
            logger.error(f"Error in store_master_status: {error}")
            self.db.conn.rollback()

    
    def check_input_file(self, case_uuid: str, input_file: str) -> bool:
        try:
            query = sql.SQL("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public' AND table_name != 'master_status' AND table_name != 'case_snapshot' AND table_name not like 'osir_%'
            """)
            self.db.cur.execute(query)
            tables = self.db.cur.fetchall()

            for table in tables:
                query = sql.SQL("""
                    SELECT 1
                    FROM {}
                    WHERE case_uuid = %s AND input_file = %s AND processing_status = 'processing_started'
                    LIMIT 1
                """).format(sql.Identifier(table[0]))
                self.db.cur.execute(query, (case_uuid, input_file))
                if self.db.cur.fetchone():
                    logger.debug(f"Query: {self.db.cur.mogrify(query, (case_uuid, input_file))}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return False

    def check_input_dir(self, case_uuid: str, input_dir: str) -> bool:
        try:
            query = sql.SQL("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public' AND table_name != 'master_status' AND table_name != 'case_snapshot'
            """)
            self.db.cur.execute(query)
            tables = self.db.cur.fetchall()

            for table in tables:
                query = sql.SQL("""
                    SELECT 1
                    FROM {}
                    WHERE case_uuid = %s AND (
                        input_dir = %s OR input_dir LIKE %s OR input_file LIKE %s
                    ) AND processing_status = 'processing_started'
                    LIMIT 1
                """).format(sql.Identifier(table[0]))
                self.db.cur.execute(query, (case_uuid, input_dir, f'{input_dir}%', f'{input_dir}%'))
                if self.db.cur.fetchone():
                    return True
            return False
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return False

    def is_processing_active(self, case_uuid: str) -> bool:
        try:
            self.db.cur.execute("""
                SELECT COUNT(*)
                FROM osir_tasks
                WHERE case_uuid = %s
                AND processing_status = 'processing_started'
            """, (str(case_uuid),))
            count = self.db.cur.fetchone()[0]
            return count > 0
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'input: {e}")
            raise

    def get_stored_case_snapshot(self, case_path: str) -> List[Tuple[str, str]]:
        case_path = str(case_path)
        query = """
        SELECT path, entry_type
        FROM case_snapshot
        WHERE case_path = %s
        """
        try:
            self.db.cur.execute(query, (case_path,))
            rows = self.db.cur.fetchall()
            logger.debug(f"Retrieved {len(rows)} entries for case_path: {case_path}")
            return [(row[0], row[1]) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching entries for case_path {case_path}: {str(e)}")
            return []

    def store_case_snapshot(self, case_uuid: str, case_path: str, entries_list: List[Tuple[str, str]]):
        try:
            case_path = str(case_path)
            case_uuid = str(case_uuid)
            delete_query = "DELETE FROM case_snapshot WHERE case_uuid = %s"
            self.db.cur.execute(delete_query, (case_uuid,))

            output = io.StringIO()
            for path, entry_type in entries_list:
                path = str(path)
                if '\\' in path:
                    logger.warning(f"Skipping entry due to invalid backslash: path={path}, entry_type={entry_type}")
                    continue
                output.write(f"{case_uuid}\t{case_path}\t{path}\t{entry_type}\n")
            output.seek(0)

            self.db.cur.copy_from(
                file=output,
                table='case_snapshot',
                columns=('case_uuid', 'case_path', 'path', 'entry_type'),
                null=''
            )
            self.db.conn.commit()
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Bulk insert error for case_uuid {case_uuid}: {str(e)}")

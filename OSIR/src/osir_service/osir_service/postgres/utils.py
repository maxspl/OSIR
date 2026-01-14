import datetime
import io
from sqlite3 import OperationalError
from typing import List, Tuple
from psycopg2 import sql
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()

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

        self.db.execute_query(f"""
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

            self.db.execute_query(update_query, values + [case_uuid, input_file, input_dir])
            logger.debug(f"Database updated record(s).")
        except Exception as error:
            logger.error(f"Error updating record: {error}")

    def store_master_status(self, case_path: str, status: str, case_uuid: str, modules_selected: str):
        case_path = str(case_path)
        current_timestamp = datetime.datetime.now()
        try:
            exists = self.db.execute_query("""
                SELECT 1 FROM master_status WHERE case_path = %s
            """, (case_path,), fetch="fetchone")

            if exists:
                self.db.execute_query("""
                    UPDATE master_status
                    SET status = %s, case_uuid = %s, timestamp = %s, modules_selected = %s
                    WHERE case_path = %s
                """, (status, case_uuid, current_timestamp, modules_selected, case_path))
            else:
                self.db.execute_query("""
                    INSERT INTO master_status (case_path, status, case_uuid, modules_selected)
                    VALUES (%s, %s, %s, %s)
                """, (case_path, status, case_uuid, modules_selected))
            action = "Updated" if exists else "Inserted"
            logger.debug(f"{action} master_status record for case_path: {case_path}")
        except Exception as error:
            logger.error(f"Error in store_master_status: {error}")
            

    
    def check_input_file(self, case_uuid: str, input_file: str) -> bool:
        try:
            query = sql.SQL("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public' AND table_name != 'master_status' AND table_name != 'case_snapshot' AND table_name not like 'osir_%'
            """)
            tables = self.db.execute_query(query, fetch="fetchall")

            for table in tables:
                query = sql.SQL("""
                    SELECT 1
                    FROM {}
                    WHERE case_uuid = %s AND input_file = %s AND processing_status = 'processing_started'
                    LIMIT 1
                """).format(sql.Identifier(table[0]))
                row = self.db.execute_query(query, (case_uuid, input_file), fetch="fetchone")
                if row:
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
            tables = self.db.execute_query(query, fetch="fetchall")

            for table in tables:
                query = sql.SQL("""
                    SELECT 1
                    FROM {}
                    WHERE case_uuid = %s AND (
                        input_dir = %s OR input_dir LIKE %s OR input_file LIKE %s
                    ) AND processing_status = 'processing_started'
                    LIMIT 1
                """).format(sql.Identifier(table[0]))
                row = self.db.execute_query(query, (case_uuid, input_dir, f'{input_dir}%', f'{input_dir}%'), fetch="fetchone")
                if row:
                    return True
            return False
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return False

    def is_processing_active(self, handler_uuid: str) -> bool:
        try:
            count = self.db.execute_query("""
                SELECT
                    COUNT(t.task_id)
                FROM
                    osir_handlers h
                JOIN
                    unnest(h.task_id) AS task_id_unpacked ON TRUE
                JOIN
                    osir_tasks t ON t.task_id = task_id_unpacked
                WHERE handler_id = %s AND t.processing_status IN ('processing_started', 'task_created');
            """, (str(handler_uuid),), fetch="fetchone")[0]

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
            rows = self.db.execute_query(query, (case_path,), fetch="fetchall")
            logger.debug(f"Retrieved {len(rows)} entries for case_path: {case_path}")
            return [(row[0], row[1]) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching entries for case_path {case_path}: {str(e)}")
            return []

    def store_case_snapshot(self, case_uuid: str, case_path: str, entries_list: List[Tuple[str, str]]):
        try:
            case_path = str(case_path)
            case_uuid = str(case_uuid)
            
            # Nettoyage initial
            self.db.execute_query("DELETE FROM case_snapshot WHERE case_uuid = %s", (case_uuid,))

            # --- DÉDOUBLONNAGE ---
            # Utiliser un set pour garder trace des chemins déjà vus
            seen_paths = set()
            unique_entries = []
            
            for path, entry_type in entries_list:
                path = str(path)
                # On ignore les backslashes et les doublons exacts (case_uuid + path)
                if '\\' in path:
                    continue
                if path not in seen_paths:
                    seen_paths.add(path)
                    unique_entries.append((path, entry_type))

            # Génération du buffer avec les entrées uniques
            output = io.StringIO()
            for path, entry_type in unique_entries:
                output.write(f"{case_uuid}\t{case_path}\t{path}\t{entry_type}\n")
            output.seek(0)

            conn = self.db._ensure_connection()
            if not conn:
                raise OperationalError("Could not establish a database connection.")

            # 2. Execute the query
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

import json
import uuid
from typing import List, Union, Optional
from osir_service.postgres.PostgresConstants import ProcessingStatus
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()

class TaskManager:
    def __init__(self, db_osir):
        self.db = db_osir

    def create_table(self):
        try:
            type_exists = self.db.execute_query("""
                SELECT 1 FROM pg_type WHERE typname = 'processing_status_enum'
            """, fetch="fetchone")
            

            if not type_exists:
                self.db.execute_query("""
                    CREATE TYPE processing_status_enum AS ENUM (
                        'task_created',
                        'processing_started',
                        'processing_done',
                        'processing_failed'
                    );
                """)

            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS osir_tasks (
                    task_id UUID PRIMARY KEY,
                    case_uuid UUID,
                    agent TEXT,
                    module TEXT,
                    input TEXT,
                    processing_status processing_status_enum DEFAULT 'task_created',
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    trace JSONB DEFAULT '{}'::jsonb
                )
            """)
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            raise

    def create(self, case_uuid: str, agent: str, module: str, input: str, task_id: Optional[str] = None) -> str:
        try:
            if task_id is None:
                task_id = str(uuid.uuid4())

            self.db.execute_query("""
                INSERT INTO osir_tasks (
                    task_id,
                    case_uuid,
                    agent,
                    module,
                    input,
                    processing_status
                )
                VALUES (%s, %s, %s, %s, %s, 'task_created')
            """, (task_id, case_uuid, agent, module, input))

            logger.debug(f"Task created successfully with task_id: {task_id}")
            return task_id
        except Exception as e:
            
            logger.error(f"Error creating task: {e}")
            raise

    def get(self, task_id: str) -> dict:
        if not task_id or task_id.strip() == "":
            logger.debug("Get called with empty task_id, skipping query.")
            return None

        try:
            row = self.db.execute_query("""
                SELECT task_id, case_uuid, agent, module, input, processing_status, timestamp, trace 
                FROM osir_tasks
                WHERE task_id = %s
            """, (task_id,), fetch="fetchone")
            
            if row:
                return self._row_to_dict(row)
            return None
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {e}")
            raise

    def list(
        self,
        case_uuid: Optional[str] = None,
        processing_status: Optional[Union[str, List[str]]] = None,
        exclude_status: Optional[Union[str, List[str]]] = None
    ) -> list:
        try:
            def to_list(value):
                return [value] if isinstance(value, str) else value

            if processing_status:
                processing_status = to_list(processing_status)
            if exclude_status:
                exclude_status = to_list(exclude_status)

            # --- Modification ici : On liste les colonnes explicitement ---
            query = """
                SELECT task_id, case_uuid, agent, module, input, processing_status, timestamp 
                FROM osir_tasks
            """
            conditions = []
            params = []

            if case_uuid:
                conditions.append("case_uuid = %s")
                params.append(case_uuid)

            if processing_status:
                placeholders = ", ".join(["%s"] * len(processing_status))
                conditions.append(f"processing_status IN ({placeholders})")
                params.extend(processing_status)

            if exclude_status:
                placeholders = ", ".join(["%s"] * len(exclude_status))
                conditions.append(f"processing_status NOT IN ({placeholders})")
                params.extend(exclude_status)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            rows = self.db.execute_query(query, params, fetch="fetchall")
            
            # On passe les lignes à _row_to_dict
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            raise

    def _row_to_dict(self, row) -> dict:
        d = {
            "task_id": str(row[0]),
            "case_uuid": str(row[1]) if row[1] else None,
            "agent": row[2],
            "module": row[3],
            "input": row[4],
            "processing_status": row[5],
            "timestamp": row[6]
        }
        
        # Si la requête contenait la colonne trace (index 7), on l'ajoute
        if len(row) > 7:
            d["trace"] = row[7]
            
        return d

    def update(
        self,
        task_id: str,
        processing_status: ProcessingStatus,
        trace_data: Optional[dict] = None,
        agent: Optional[str] = None
    ) -> Optional[dict]: # Changed return type hint as you return the row
        try:
            # 1. Prepare fields and parameters dynamically
            updates = ["processing_status = %s"]
            params = [processing_status.value]

            if agent is not None:
                updates.append("agent = %s")
                params.append(agent)

            # Handle trace: Use COALESCE to keep old trace if new trace is None
            trace_json = json.dumps(trace_data) if trace_data else None
            updates.append("trace = COALESCE(%s, trace)")
            params.append(trace_json)

            # Issue with threaded request
            fix_thread = "" 
            if processing_status.value == "processing_started":
                fix_thread = "AND processing_status != 'processing_done' AND processing_status != 'processing_failed'"
            # 2. Build the final query
            query = f"""
                UPDATE osir_tasks 
                SET {', '.join(updates)} 
                WHERE task_id = %s {fix_thread}
            """
            params.append(task_id)

            # 3. Execute
            updated_row = self.db.execute_query(query, tuple(params))

            return updated_row

        except Exception as e:
            logger.error(f"Error during update for task {task_id}: {e}")
            raise
    
    def check_input(self, case_uuid: str, input: str) -> bool:
        input_str = str(input)
        
        result = self.db.execute_query("""
            SELECT COUNT(*)
            FROM osir_tasks
            WHERE case_uuid = %s
            AND input = %s
            AND processing_status = 'processing_started'
        """, (case_uuid, input_str), fetch="fetchone")

        # VALIDATION: Result must be a tuple with exactly 1 item
        if result is None or not isinstance(result, (tuple, list)):
            return False
            
        if len(result) != 1:
            logger.error(f"Integrity Error: Expected 1 column (count), got {len(result)}. Value: {result}")
            return False

        count = result[0]
        
        # If count is a UUID (string) instead of an int, the reset logic failed
        if not isinstance(count, int):
            logger.error(f"Type Error: Count is {type(count)} (Value: {count}). Resetting connection state recommended.")
            return False

        return count > 0
    
    def delete(self, task_id: Optional[str] = None, case_uuid: Optional[str] = None, handler_id: Optional[str] = None) -> bool:
        """
        Supprime des tâches de la table osir_tasks en utilisant task_id, case_uuid ou handler_id.

        Args:
            task_id (Optional[str]): L'ID de la tâche à supprimer.
            case_uuid (Optional[str]): L'UUID du cas.
            handler_id (Optional[str]): L'ID du handler dont on veut supprimer les tâches liées.

        Returns:
            bool: True si la suppression a réussi.
        """
        try:
            if not any([task_id, case_uuid, handler_id]):
                raise ValueError("Au moins un paramètre (task_id, case_uuid ou handler_id) doit être fourni.")

            if task_id:
                # Supprimer une tâche spécifique
                self.db.execute_query("""
                    DELETE FROM osir_tasks
                    WHERE task_id = %s
                """, (task_id,))
                logger.debug(f"Tâche avec l'ID {task_id} supprimée.")

            elif case_uuid:
                # Supprimer toutes les tâches associées à un cas
                self.db.execute_query("""
                    DELETE FROM osir_tasks
                    WHERE case_uuid = %s
                """, (case_uuid,))
                logger.debug(f"Tâches associées au cas {case_uuid} supprimées.")

            elif handler_id:
                # Supprimer les tâches dont l'ID est présent dans la liste task_id du handler
                self.db.execute_query("""
                    DELETE FROM osir_tasks
                    WHERE task_id = ANY(
                        SELECT unnest(task_id)
                        FROM osir_handlers
                        WHERE handler_id = %s
                    )
                """, (handler_id,))
                logger.debug(f"Tâches associées au handler {handler_id} supprimées.")

            return True

        except ValueError as ve:
            logger.error(f"Erreur de validation: {ve}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la suppression : {e}")
            raise
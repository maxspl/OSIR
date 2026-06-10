import uuid
from typing import List, Union, Optional
from osir_service.postgres.model.OsirDbTaskModel import OsirDbTaskModel
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()


# ----------------------------------------------------------------------
# Effective task view.
#
# celery_taskmeta (written by the Celery database result backend) is the
# source of truth for task state. The legacy processing_status column on
# osir_tasks only acts as a fallback: pre-migration rows keep their final
# status there, and its 'task_created' default is exactly the right answer
# for tasks Celery has not reported yet (PENDING tasks have no row).
# ----------------------------------------------------------------------
TASK_VIEW_SELECT = """
    SELECT
        t.task_id,
        t.case_uuid,
        t.handler_id,
        COALESCE(NULLIF(t.agent, 'Null'), m.worker, 'Null') AS agent,
        t.module,
        t.input,
        t.output,
        CASE
            WHEN m.status = 'SUCCESS'                         THEN 'processing_done'
            WHEN m.status IN ('FAILURE', 'REVOKED')           THEN 'processing_failed'
            WHEN m.status IN ('STARTED', 'RETRY', 'RECEIVED') THEN 'processing_started'
            WHEN m.status IS NOT NULL                         THEN 'task_created'
            ELSE t.processing_status::text
        END AS processing_status,
        t.timestamp,
        CASE
            WHEN t.trace IS NOT NULL AND t.trace <> '{}'::jsonb THEN t.trace
            WHEN m.traceback IS NOT NULL THEN
                jsonb_build_object('logs', to_jsonb(string_to_array(m.traceback, chr(10))))
            ELSE '{}'::jsonb
        END AS trace,
        m.result AS celery_result
    FROM osir_tasks t
    LEFT JOIN celery_taskmeta m ON m.task_id = t.task_id::text
"""

# Celery states meaning "this task is over".
CELERY_DONE_STATES = "('SUCCESS', 'FAILURE', 'REVOKED')"


def _decode_result_trace(row: dict) -> dict:
    """Overlay the module trace stored in the (pickled) celery result onto
    the trace field for detail views. Successful tasks return their log
    blob as the task result; failures are covered by celery's traceback
    (or by the pickled exception when no traceback string was stored)."""
    try:
        blob = row.get("celery_result")
        if blob and (not row.get("trace") or row["trace"] == {}):
            import pickle
            decoded = pickle.loads(bytes(blob))
            if isinstance(decoded, dict) and "logs" in decoded:
                row["trace"] = decoded
            elif isinstance(decoded, BaseException):
                row["trace"] = {"logs": [f"{type(decoded).__name__}: {decoded}"]}
            elif isinstance(decoded, dict) and decoded.get("exc_message"):
                msg = decoded["exc_message"]
                msg = msg if isinstance(msg, (list, tuple)) else [msg]
                row["trace"] = {"logs": [f"{decoded.get('exc_type', 'Error')}: {m}" for m in msg]}
    except Exception:
        pass
    row.pop("celery_result", None)
    return row


class OsirDbTask:
    """
        Manages the lifecycle of tasks stored in the PostgreSQL 'osir_tasks' table,
        including table creation, task creation, retrieval, updates, and deletion.
    """

    def __init__(self, db_osir):
        self.db = db_osir

    def create_table(self):
        """
            Creates the 'osir_tasks' table and the custom ENUM type 'processing_status_enum' 
            if they do not already exist.

            Raises:
                Exception: If the database query fails.
        """
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
                    handler_id UUID,
                    agent TEXT,
                    module TEXT,
                    input TEXT,
                    output TEXT DEFAULT 'N/A',
                    processing_status processing_status_enum DEFAULT 'task_created',
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    trace JSONB DEFAULT '{}'::jsonb
                )
            """)

            # Add handler_id (link task -> handler) on older tables, and index it.
            self.db.execute_query(
                "ALTER TABLE osir_tasks ADD COLUMN IF NOT EXISTS handler_id UUID"
            )
            self.db.execute_query(
                "CREATE INDEX IF NOT EXISTS idx_osir_tasks_handler_id "
                "ON osir_tasks (handler_id, processing_status)"
            )
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            raise

    def create_celery_tables(self):
        """
            Creates the Celery database result-backend tables if they do not
            exist yet, with a schema identical to the one Celery's SQLAlchemy
            backend would create (so SQLAlchemy's checkfirst create_all is a
            no-op). Doing it here guarantees the JOIN queries work on a fresh
            database even before any worker reported a result.
        """
        try:
            self.db.execute_query("CREATE SEQUENCE IF NOT EXISTS task_id_sequence")
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS celery_taskmeta (
                    id INTEGER NOT NULL DEFAULT nextval('task_id_sequence') PRIMARY KEY,
                    task_id VARCHAR(155) UNIQUE,
                    status VARCHAR(50),
                    result BYTEA,
                    date_done TIMESTAMP WITHOUT TIME ZONE,
                    traceback TEXT,
                    name VARCHAR(155),
                    args BYTEA,
                    kwargs BYTEA,
                    worker VARCHAR(155),
                    retries INTEGER,
                    queue VARCHAR(155)
                )
            """)
            self.db.execute_query("CREATE SEQUENCE IF NOT EXISTS taskset_id_sequence")
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS celery_tasksetmeta (
                    id INTEGER NOT NULL DEFAULT nextval('taskset_id_sequence') PRIMARY KEY,
                    taskset_id VARCHAR(155) UNIQUE,
                    result BYTEA,
                    date_done TIMESTAMP WITHOUT TIME ZONE
                )
            """)
        except Exception as e:
            logger.error(f"Error creating celery result tables: {e}")
            raise

    def create(self, case_uuid: str, agent: str, module: str, input: str, output: str = 'N/A', task_id: Optional[str] = None, handler_id: Optional[str] = None) -> str:        
        """
            Inserts a new task into the database.

            Args:
                case_uuid (str): The UUID of the case associated with the task.
                agent (str): The name or identifier of the agent performing the task.
                module (str): The specific module responsible for the execution.
                input (str): The input data or configuration for the task.
                output (str): The output path of the module
                task_id (str, optional): A specific UUID for the task. If None, a new UUID is generated.
                handler_id (str, optional): The handler this task belongs to. Stored on the task row so handler -> tasks lookups are simple indexed queries.
 
            Returns:
                str: The UUID of the created task.

            Raises:
                Exception: If the database insertion fails.
        """
        try:
            if task_id is None:
                task_id = str(uuid.uuid4())

            self.db.execute_query("""
                INSERT INTO osir_tasks (
                    task_id,
                    case_uuid,
                    handler_id,
                    agent,
                    module,
                    input,
                    output,
                    processing_status
                )

                VALUES (%s, %s, %s, %s, %s, %s, %s, 'task_created')
            """, (task_id, case_uuid, handler_id, agent, module, input, output))

            logger.debug(f"Task created successfully with task_id: {task_id}")
            return task_id
        except Exception as e:

            logger.error(f"Error creating task: {e}")
            raise

    def create_bulk(self, rows: List[tuple]) -> int:
        """
            Inserts many tasks in a single round trip (execute_values).

            Args:
                rows: list of tuples
                    (task_id, case_uuid, handler_id, agent, module, input)

                'output' defaults to 'N/A' and 'processing_status' to
                'task_created', matching create().

            Returns:
                int: number of rows inserted.
        """
        if not rows:
            return 0

        try:
            self.db.execute_values_query(
                """
                INSERT INTO osir_tasks (
                    task_id,
                    case_uuid,
                    handler_id,
                    agent,
                    module,
                    input,
                    output,
                    processing_status
                )
                VALUES %s
                """,
                rows,
                template="(%s, %s, %s, %s, %s, %s, 'N/A', 'task_created')",
            )
            logger.debug(f"Bulk task insert: {len(rows)} row(s)")
            return len(rows)
        except Exception as e:
            logger.error(f"Error bulk-creating tasks: {e}")
            raise

    def get(self, task_id: str) -> OsirDbTaskModel:
        """
            Retrieves a single task's details by its UUID.

            Args:
                task_id (str): The UUID of the task to retrieve.

            Returns:
                Union[dict, None]: A dictionary containing task details, or None if no task is found or task_id is empty.

            Raises:
                Exception: If the database query fails.
        """
        if not task_id or task_id.strip() == "":
            logger.debug("Get called with empty task_id, skipping query.")
            return None

        try:
            row = self.db.execute_query(
                TASK_VIEW_SELECT + " WHERE t.task_id = %s",
                (task_id,), fetch="fetchone"
            )

            if not row:
                return None

            return OsirDbTaskModel.model_validate(_decode_result_trace(dict(row)))
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {e}")
            raise
    
    def get_by_output(self, output: str) -> OsirDbTaskModel:
        """
            Retrieves a single task's details by its output.
            Args:
                output (str): The output value to search for.
            Returns:
                Union[dict, None]: A dictionary containing task details, or None if no task is found.
            Raises:
                Exception: If the database query fails.
        """
        if not output or output.strip() == "":
            logger.debug("get_by_output called with empty output, skipping query.")
            return None
        try:
            row = self.db.execute_query(
                TASK_VIEW_SELECT + " WHERE t.output = %s",
                (output,), fetch="fetchone"
            )
            if not row:
                return None
            return OsirDbTaskModel.model_validate(_decode_result_trace(dict(row)))
        except Exception as e:
            logger.error(f"Error fetching task by output {output}: {e}")
            raise

    def list(
        self,
        case_uuid: Optional[str] = None,
        processing_status: Optional[Union[str, List[str]]] = None,
        exclude_status: Optional[Union[str, List[str]]] = None
    ) -> List[OsirDbTaskModel]:
        """
        Lists tasks based on filtering criteria such as case UUID or status.

            Args:
                case_uuid (str, optional): Filter tasks by a specific case UUID.
                processing_status (Union[str, List[str]], optional): Include only tasks with these statuses.
                exclude_status (Union[str, List[str]], optional): Exclude tasks with these statuses.

            Returns:
                list: A list of dictionaries, each representing a task.

            Raises:
                Exception: If the database query fails.
        """
        try:
            def to_list(value):
                return [value] if isinstance(value, str) else value

            if processing_status:
                processing_status = to_list(processing_status)
            if exclude_status:
                exclude_status = to_list(exclude_status)

            query = f"SELECT * FROM ({TASK_VIEW_SELECT}) v"
            conditions = []
            params = []

            if case_uuid:
                conditions.append("v.case_uuid = %s")
                params.append(case_uuid)

            if processing_status:
                placeholders = ", ".join(["%s"] * len(processing_status))
                conditions.append(f"v.processing_status IN ({placeholders})")
                params.extend(processing_status)

            if exclude_status:
                placeholders = ", ".join(["%s"] * len(exclude_status))
                conditions.append(f"v.processing_status NOT IN ({placeholders})")
                params.extend(exclude_status)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY v.timestamp DESC LIMIT 200"
            rows = self.db.execute_query(query, params, fetch="fetchall")

            return [OsirDbTaskModel.model_validate(_decode_result_trace(dict(x))) for x in rows]
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            raise

    def set_runtime_info(self, task_id: str, agent: Optional[str] = None, output: Optional[str] = None) -> None:
        """
            Records runtime metadata that only the worker knows (the resolved
            output path and the worker name). This is the single per-task
            write left outside the Celery result backend: status transitions
            and tracebacks live in celery_taskmeta.

            Args:
                task_id (str): The UUID of the task.
                agent (str, optional): Worker name executing the task.
                output (str, optional): Resolved output path of the module.
        """
        updates = []
        params = []

        if agent is not None:
            updates.append("agent = %s")
            params.append(agent)
        if output is not None:
            updates.append("output = %s")
            params.append(output)

        if not updates:
            return

        params.append(task_id)
        try:
            self.db.execute_query(
                f"UPDATE osir_tasks SET {', '.join(updates)} WHERE task_id = %s",
                tuple(params)
            )
        except Exception as e:
            logger.error(f"Error setting runtime info for task {task_id}: {e}")
            raise

    def check_input(self, case_uuid: str, input: str, exclude_task_id: Optional[str] = None) -> bool:
        """
            Checks if the input is already used by another active task.

            When called from inside a Celery task, several tasks with the same
            input can already be marked STARTED at the same time. Blocking on
            any other STARTED task creates a deadlock: task A waits for task B,
            while task B waits for task A.

            To avoid this, the task currently running only waits for older
            active tasks with the same input. The oldest task is allowed to run,
            then younger tasks are released one by one.

            Args:
                case_uuid (str): The UUID of the case.
                input (str): The input string to check for duplicates.
                exclude_task_id (str, optional): Current task UUID. When set,
                    it is used both to exclude the current task and to apply a
                    deterministic ordering between active tasks.

            Returns:
                bool: True if an older matching active task is found, False otherwise.
        """
        input_str = str(input)

        try:
            if exclude_task_id:
                result = self.db.execute_query("""
                    WITH current_task AS (
                        SELECT task_id, timestamp
                        FROM osir_tasks
                        WHERE task_id = %s::uuid
                    )
                    SELECT COUNT(*) AS count
                    FROM osir_tasks t
                    JOIN celery_taskmeta m ON m.task_id = t.task_id::text
                    CROSS JOIN current_task ct
                    WHERE t.case_uuid = %s
                      AND t.input = %s
                      AND m.status IN ('STARTED', 'RETRY')
                      AND t.task_id <> ct.task_id
                      AND (
                          t.timestamp < ct.timestamp
                          OR (
                              t.timestamp = ct.timestamp
                              AND t.task_id::text < ct.task_id::text
                          )
                      )
                """, (exclude_task_id, case_uuid, input_str), fetch="fetchone")
            else:
                result = self.db.execute_query("""
                    SELECT COUNT(*) AS count
                    FROM osir_tasks t
                    JOIN celery_taskmeta m ON m.task_id = t.task_id::text
                    WHERE t.case_uuid = %s
                      AND t.input = %s
                      AND m.status IN ('STARTED', 'RETRY')
                """, (case_uuid, input_str), fetch="fetchone")
        except Exception as e:
            logger.error(f"Error checking active input usage: {e}")
            return False

        if not result or "count" not in result:
            return False

        return result["count"] > 0

    def delete(self, task_id: Optional[str] = None, case_uuid: Optional[str] = None, handler_id: Optional[str] = None) -> bool:
        """
            Deletes tasks from the table based on either task_id, case_uuid, or handler_id.

            Args:
                task_id (str, optional): The ID of the specific task to delete.
                case_uuid (str, optional): The UUID of the case to delete all related tasks for.
                handler_id (str, optional): The ID of the handler whose tasks should be deleted.

            Returns:
                bool: True if the deletion was successful.

            Raises:
                ValueError: If none of the optional parameters are provided.
                Exception: If the deletion query fails.
        """
        try:
            if not any([task_id, case_uuid, handler_id]):
                raise ValueError("Au moins un paramètre (task_id, case_uuid ou handler_id) doit être fourni.")

            if task_id:
                cond, params = "task_id = %s", (task_id,)
                log_msg = f"Tâche avec l'ID {task_id} supprimée."
            elif case_uuid:
                cond, params = "case_uuid = %s", (case_uuid,)
                log_msg = f"Tâches associées au cas {case_uuid} supprimées."
            else:
                cond, params = "handler_id = %s", (handler_id,)
                log_msg = f"Tâches associées au handler {handler_id} supprimées."

            # Purge the matching Celery result rows first (they reference
            # osir_tasks by task_id), then the task rows themselves.
            self.db.execute_query(f"""
                DELETE FROM celery_taskmeta
                WHERE task_id IN (
                    SELECT task_id::text FROM osir_tasks WHERE {cond}
                )
            """, params)
            self.db.execute_query(f"DELETE FROM osir_tasks WHERE {cond}", params)
            logger.debug(log_msg)

            return True

        except ValueError as ve:
            logger.error(f"Erreur de validation: {ve}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la suppression : {e}")
            raise

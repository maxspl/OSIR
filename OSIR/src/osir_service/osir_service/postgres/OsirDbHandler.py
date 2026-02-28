import uuid
from typing import Union, Optional, List
from osir_lib.logger import AppLogger
from osir_service.postgres.model.OsirDbHandlerModel import OsirDbHandlerModel

logger = AppLogger().get_logger()


class OsirDbHandler:
    """
        Manages high-level execution handlers within the OSIR database.

        A 'Handler' represents a grouped execution of one or more forensic modules 
        for a specific case.
    """

    def __init__(self, db_osir):
        """
            Initializes the OsirDbHandler with a database connection.
        """
        self.db = db_osir

    def create_table(self):
        """
            Initializes the 'osir_handlers' table in PostgreSQL.
        """
        try:
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS osir_handlers (
                    handler_id UUID PRIMARY KEY,
                    case_uuid UUID NOT NULL,
                    modules TEXT[],
                    task_id UUID[],
                    processing_status VARCHAR(50) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            # logger.info("Table `osir_handlers` initialized successfully.")
        except Exception as e:
            logger.error(f"Error creating `osir_handlers` table: {e}")
            raise

    def create(self, case_uuid: str, modules: List[str], task_ids: List[str], handler_id: uuid.UUID = None) -> OsirDbHandlerModel:
        """
            Registers a new execution handler.

            Args:
                case_uuid (str): The UUID of the investigation case.
                modules (List[str]): Names of the modules included in this execution.
                task_ids (List[str]): Initial Celery task IDs associated with this handler.
                handler_id (uuid.UUID, optional): A specific UUID to use, otherwise a new one is generated.

            Returns:
                str: The unique handler_id.
        """
        try:
            if not handler_id:
                handler_id = uuid.uuid4()
            self.db.execute_query("""
                INSERT INTO osir_handlers (
                    handler_id,
                    case_uuid,
                    modules,
                    task_id,
                    processing_status
                )
                VALUES (%s, %s, %s, %s, 'processing_started')
            """, (handler_id, case_uuid, modules, task_ids))

            logger.debug(f"Handler successfully created: {handler_id}")
            return OsirDbHandlerModel(
                handler_id=handler_id,
                case_uuid=case_uuid,
                modules=modules,
                task_id=task_ids,
                processing_status='processing_started'
            ) 
        except Exception as e:
            logger.error(f"Error creating handler: {e}")
            raise

    def list(
        self,
        case_uuid: Optional[str] = None,
        processing_status: Optional[Union[str, List[str]]] = None,
        exclude_status: Optional[Union[str, List[str]]] = None
    ) -> List[OsirDbHandlerModel]:
        """
        Retrieves a filtered list of handlers, joining with case metadata.
        """
        try:
            query = """
                SELECT h.*, c.name AS case_name
                FROM osir_handlers h
                LEFT JOIN osir_case c ON h.case_uuid = c.case_uuid
            """
            conditions = []
            params = []

            if case_uuid:
                uuid_value = case_uuid if isinstance(case_uuid, uuid.UUID) else uuid.UUID(case_uuid)
                conditions.append("h.case_uuid = %s")
                params.append(uuid_value)

            if processing_status:
                if isinstance(processing_status, str):
                    conditions.append("h.processing_status = %s")
                    params.append(processing_status)
                else:
                    placeholders = ", ".join(["%s"] * len(processing_status))
                    conditions.append(f"h.processing_status IN ({placeholders})")
                    params.extend(processing_status)

            if exclude_status:
                if isinstance(exclude_status, str):
                    conditions.append("h.processing_status != %s")
                    params.append(exclude_status)
                else:
                    placeholders = ", ".join(["%s"] * len(exclude_status))
                    conditions.append(f"h.processing_status NOT IN ({placeholders})")
                    params.extend(exclude_status)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            rows = self.db.execute_query(query, params, fetch="fetchall")

            if not rows:
                return None
            
            return [OsirDbHandlerModel.model_validate(x) for x in rows]

        except Exception as e:
            logger.error(f"Error fetching handler list: {e}")
            raise

    def get(self, handler_id: Optional[str] = None, case_uuid: Optional[str] = None) -> Union[OsirDbHandlerModel, List[OsirDbHandlerModel], None]:
        """
        Retrieves one or more handlers by ID or Case UUID.
        """
        try:
            rows = None
            if isinstance(case_uuid, str):
                case_uuid = uuid.UUID(case_uuid)

            if handler_id:
                rows = self.db.execute_query("SELECT * FROM osir_handlers WHERE handler_id = %s::uuid", (handler_id,), fetch="fetchall")
            elif case_uuid:
                rows = self.db.execute_query("SELECT * FROM osir_handlers WHERE case_uuid = %s", (case_uuid,), fetch="fetchall")
            else:
                raise ValueError("Must provide either `handler_id` or `case_uuid`.")

            if not rows:
                return {"case_uuid": case_uuid, "handler_id": handler_id, "modules": None, "task_ids": None, "processing_status": None}

            if handler_id:
                return OsirDbHandlerModel.model_validate(rows[0])
            else:
                return [OsirDbHandlerModel.model_validate(x) for x in rows]
        except Exception as e:
            logger.error(f"Error retrieving handlers: {e}")
            raise

    def update(self, handler_id: str, processing_status: str) -> bool:
        """Updates the global status of a handler."""
        try:
            self.db.execute_query("UPDATE osir_handlers SET processing_status = %s WHERE handler_id = %s", (processing_status, handler_id))
            logger.debug(f"Handler {handler_id} status updated successfully.")
            return True
        except Exception as e:
            logger.error(f"Error updating handler {handler_id} status: {e}")
            raise

    def append_task_ids(self, handler_id: str, new_task_ids: List[str]) -> bool:
        """
        Dynamically adds new Celery task IDs to an existing handler.
        Useful when a module discovery process triggers additional tasks.
        """
        try:
            result = self.get(handler_id=handler_id) 
            if result is None:
                logger.error(f"No handler found with ID {handler_id}.")
                return False

            current_task_ids = result.task_id
            if isinstance(current_task_ids, str):
                current_task_ids = [current_task_ids]

            # Normalize and deduplicate UUIDs
            updated_task_ids = list(set([uuid.UUID(tid) if isinstance(tid, str) else tid for tid in (current_task_ids + new_task_ids)]))

            self.db.execute_query("UPDATE osir_handlers SET task_id = %s WHERE handler_id = %s", (updated_task_ids, handler_id))
            logger.debug(f"Task IDs for handler {handler_id} updated successfully.")
            return True
        except Exception as e:
            logger.error(f"Error updating task IDs for handler {handler_id}: {e}")
            raise

    def delete(self, handler_id: Optional[str] = None, case_uuid: Optional[str] = None, task_id: Optional[str] = None) -> bool:
        """
        Deletes handlers or removes specific task references.
        """
        try:
            if not handler_id and not case_uuid and not task_id:
                raise ValueError("Must provide `handler_id`, `case_uuid`, or `task_id`.")

            if handler_id:
                self.db.execute_query("DELETE FROM osir_handlers WHERE handler_id = %s", (handler_id,))
                logger.debug(f"Handler {handler_id} deleted.")
            elif case_uuid:
                if isinstance(case_uuid, str):
                    case_uuid = uuid.UUID(case_uuid)
                self.db.execute_query("DELETE FROM osir_handlers WHERE case_uuid = %s", (case_uuid,))
                logger.debug(f"All handlers for case {case_uuid} deleted.")
            elif task_id:
                # Remove a single task ID from the array instead of deleting the row
                self.db.execute_query("UPDATE osir_handlers SET task_id = array_remove(task_id, %s) WHERE %s = ANY(task_id)", (task_id, task_id))
                logger.debug(f"Task ID {task_id} removed from handlers.")
            return True
        except Exception as e:
            logger.error(f"Error during deletion: {e}")
            raise

    def check_handler_failure(self, handler_id: str) -> bool:
        """
        Aggregates task health: returns True if any associated task has failed.
        """
        query = """
            SELECT EXISTS (
                SELECT 1 
                FROM osir_tasks 
                WHERE task_id = ANY(
                    SELECT unnest(task_id)
                    FROM osir_handlers 
                    WHERE handler_id = %s
                )
                AND processing_status = 'processing_failed'
            );
        """
        result = self.db.execute_query(query, (handler_id,), fetch="fetchone")
        return result['exists']

    def is_processing_active(self, handler_uuid: str) -> bool:
        """
            Checks if any tasks associated with a specific handler are still in a 
            pending or active state.

            Args:
                handler_uuid (str): The UUID of the handler to check.

            Returns:
                bool: True if any associated tasks are 'task_created' or 'processing_started'.

            Raises:
                Exception: If the join query between handlers and tasks fails.
        """
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
            """, (str(handler_uuid),), fetch="fetchone")['count']

            return count > 0
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'input: {e}")
            raise

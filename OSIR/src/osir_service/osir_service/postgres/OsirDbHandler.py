import uuid
from typing import Union, Optional, List
from osir_lib.logger import AppLogger
from osir_service.postgres.model.OsirDbHandlerModel import OsirDbHandlerModel
from osir_service.postgres.model.OsirDbTaskModel import OsirDbTaskModel

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
            else:
                existing_handler = self.db.execute_query(
                    "SELECT handler_id, case_uuid, modules, task_id, processing_status, created_at FROM osir_handlers WHERE handler_id = %s",
                    (handler_id,),
                    fetch="fetchone"
                )

                if existing_handler:
                    return OsirDbHandlerModel.model_validate(existing_handler)
            
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

    def _task_ids_for_handler(self, handler_id) -> List[uuid.UUID]:
        """
        Returns the task ids belonging to a handler from osir_tasks.

        """
        if not handler_id:
            return []
        rows = self.db.execute_query(
            "SELECT task_id FROM osir_tasks WHERE handler_id = %s::uuid",
            (str(handler_id),),
            fetch="fetchall",
        )
        return [row["task_id"] for row in (rows or [])]

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
                model = OsirDbHandlerModel.model_validate(rows[0])
                model.task_id = self._task_ids_for_handler(model.handler_id)
                return model
            else:
                models = [OsirDbHandlerModel.model_validate(x) for x in rows]
                for model in models:
                    model.task_id = self._task_ids_for_handler(model.handler_id)
                return models
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
                # Unlink a single task from its handler. The relationship lives on
                # the task row, so detaching = clearing osir_tasks.handler_id.
                self.db.execute_query("UPDATE osir_tasks SET handler_id = NULL WHERE task_id = %s", (task_id,))
                logger.debug(f"Task ID {task_id} unlinked from its handler.")
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
                WHERE handler_id = %s::uuid
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
                SELECT COUNT(*)
                FROM osir_tasks
                WHERE handler_id = %s::uuid
                  AND processing_status IN ('processing_started', 'task_created');
            """, (str(handler_uuid),), fetch="fetchone")['count']

            return count > 0
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'input: {e}")
            raise
    
    def get_all_task_logs(self, handler_uuid: str) -> List[OsirDbTaskModel]:
        """
            Retrieves all tasks associated with a specific handler.

            Args:
                handler_uuid (str): The UUID of the handler to filter by.

            Returns:
                list[OsirDbTask]: List of tasks associated with the handler.

            Raises:
                Exception: If the query fails.
        """
        try:
            tasks = self.db.execute_query("""
                SELECT
                    task_id,
                    case_uuid,
                    handler_id,
                    agent,
                    module,
                    input,
                    output,
                    processing_status,
                    timestamp,
                    trace
                FROM
                    osir_tasks
                WHERE
                    handler_id = %s::uuid
            """, (str(handler_uuid),), fetch="fetchall")

            return [OsirDbTaskModel.model_validate(x) for x in tasks]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des logs des tâches: {e}")
            raise
            
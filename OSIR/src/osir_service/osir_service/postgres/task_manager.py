import uuid
from typing import Union, Optional
from osir_service.postgres.PostgresConstants import ProcessingStatus
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

class TaskManager:
    def __init__(self, db_osir):
        self.db = db_osir

    def create_table(self):
        try:
            self.db.cur.execute("""
                SELECT 1 FROM pg_type WHERE typname = 'processing_status_enum'
            """)
            type_exists = self.db.cur.fetchone() is not None

            if not type_exists:
                self.db.cur.execute("""
                    CREATE TYPE processing_status_enum AS ENUM (
                        'task_created',
                        'processing_started',
                        'processing_done',
                        'processing_failed'
                    );
                """)

            self.db.cur.execute("""
                CREATE TABLE IF NOT EXISTS osir_tasks (
                    task_id UUID PRIMARY KEY,
                    case_uuid UUID,
                    agent TEXT,
                    module TEXT,
                    input TEXT,
                    processing_status processing_status_enum DEFAULT 'task_created',
                    timestamp TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            self.db.conn.commit()
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            raise

    def create(self, case_uuid: str, agent: str, module: str, input: str, task_id: Optional[str] = None) -> str:
        try:
            if task_id is None:
                task_id = str(uuid.uuid4())

            self.db.cur.execute("""
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
            self.db.conn.commit()
            logger.debug(f"Task created successfully with task_id: {task_id}")
            return task_id
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Error creating task: {e}")
            raise

    def get(self, task_id: str) -> dict:
        try:
            self.db.cur.execute("""
                SELECT * FROM osir_tasks
                WHERE task_id = %s
            """, (task_id,))
            row = self.db.cur.fetchone()
            if row:
                return {
                    "task_id": str(row[0]),
                    "case_uuid": row[1],
                    "agent": row[2],
                    "module": row[3],
                    "input": row[4],
                    "processing_status": row[5],
                    "timestamp": row[6]
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching task: {e}")
            raise

    def list(self, case_uuid: Optional[str] = None) -> list:
        try:
            if case_uuid:
                self.db.cur.execute("""
                    SELECT * FROM osir_tasks
                    WHERE case_uuid = %s
                """, (case_uuid,))
            else:
                self.db.cur.execute("""
                    SELECT * FROM osir_tasks
                """)
            rows = self.db.cur.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            raise

    def _row_to_dict(self, row) -> dict:
        return {
            "task_id": str(row[0]),
            "case_uuid": row[1],
            "agent": row[2],
            "module": row[3],
            "input": row[4],
            "processing_status": row[5],
            "timestamp": row[6]
        }

    def update(self, task_id: str, processing_status: ProcessingStatus) -> bool:
        try:
            self.db.cur.execute("""
                UPDATE osir_tasks
                SET processing_status = %s
                WHERE task_id = %s
            """, (processing_status.value, task_id))
            self.db.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            raise
    
    def check_input(self, case_uuid: str, input: str) -> bool:
        """
        Vérifie si une tâche avec le même `input` et `case_uuid` est déjà en statut `processing_started`.

        Args:
            case_uuid (str): L'UUID du cas.
            input (str): L'input de la tâche.

        Returns:
            bool: True si aucune tâche n'est en cours pour cet input, False sinon.
        """
        input = str(input)
        try:
            self.db.cur.execute("""
                SELECT COUNT(*)
                FROM osir_tasks
                WHERE case_uuid = %s
                AND input = %s
                AND processing_status = 'processing_started'
            """, (case_uuid, input))

            count = self.db.cur.fetchone()[0]
            if count > 0:
                return True
            return False

        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'input: {e}")
            raise
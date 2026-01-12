import json
import uuid
from typing import List, Union, Optional
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
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    trace JSONB DEFAULT '{}'::jsonb
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
        if not task_id or task_id.strip() == "":
            logger.debug("Get called with empty task_id, skipping query.")
            return None

        try:
            self.db.cur.execute("""
                SELECT task_id, case_uuid, agent, module, input, processing_status, timestamp, trace 
                FROM osir_tasks
                WHERE task_id = %s
            """, (task_id,))
            
            row = self.db.cur.fetchone()
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

            self.db.cur.execute(query, params)
            rows = self.db.cur.fetchall()
            
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

    def update(self, task_id: str, processing_status: ProcessingStatus, trace_data: Optional[dict] = None) -> bool:
        try:
            # Si on passe un dictionnaire de trace, on le convertit en JSON string
            trace_json = json.dumps(trace_data) if trace_data else None

            self.db.cur.execute("""
                UPDATE osir_tasks
                SET processing_status = %s,
                    trace = COALESCE(%s, trace)
                WHERE task_id = %s
            """, (processing_status.value, trace_json, task_id))
            self.db.conn.commit()
            return True
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Error updating task: {e}")
            raise
    
    def check_input(self, case_uuid: str, input: str) -> bool:
        """
        Vérifie si une tâche avec le même `input` et `case_uuid` est déjà en statut `processing_started`.

        Args:
            case_uuid (str): L'UUID du cas.
            input (str): L'input de la tâche.

        Returns:
            bool: True si une tâche est en cours pour cet input, False sinon.
                En cas d'erreur, retourne False et log l'erreur.
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

            result = self.db.cur.fetchone()
            if result is None:
                return False
            count = result[0]
            return count > 0

        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'input: {e}")
            return False
    
    def delete(self, task_id: Optional[str] = None, case_uuid: Optional[str] = None) -> bool:
        """
        Supprime une ou plusieurs tâches de la table osir_tasks en utilisant soit le task_id, soit le case_uuid.

        Args:
            task_id (Optional[str]): L'ID de la tâche à supprimer.
            case_uuid (Optional[str]): L'UUID du cas dont les tâches doivent être supprimées.

        Returns:
            bool: True si la suppression a réussi, False sinon.
        """
        try:
            if not task_id and not case_uuid:
                raise ValueError("Soit un `task_id`, soit un `case_uuid` doit être fourni.")

            if task_id:
                # Supprimer une tâche spécifique
                self.db.cur.execute("""
                    DELETE FROM osir_tasks
                    WHERE task_id = %s
                """, (task_id,))
                logger.debug(f"Tâche avec l'ID {task_id} supprimée avec succès.")

            elif case_uuid:
                # Supprimer toutes les tâches associées à un cas
                self.db.cur.execute("""
                    DELETE FROM osir_tasks
                    WHERE case_uuid = %s
                """, (case_uuid,))
                logger.debug(f"Toutes les tâches associées au cas {case_uuid} ont été supprimées avec succès.")

            self.db.conn.commit()
            return True
        except ValueError as ve:
            logger.error(f"Erreur de validation: {ve}")
            raise
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Erreur lors de la suppression de la tâche: {e}")
            raise
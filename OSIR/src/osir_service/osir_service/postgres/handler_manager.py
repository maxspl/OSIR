import uuid
from typing import Union, Optional, List, Dict
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

class HandlerManager:
    def __init__(self, db_osir):
        self.db = db_osir

    def create_table(self):
        try:
            self.db.cur.execute("""
                CREATE TABLE IF NOT EXISTS osir_handlers (
                    handler_id UUID PRIMARY KEY,
                    case_uuid UUID NOT NULL,
                    modules TEXT[],
                    task_id UUID[],
                    processing_status VARCHAR(50) NOT NULL
                );
            """)
            self.db.conn.commit()
            logger.info("Table `osir_handlers` créée avec succès.")
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Erreur lors de la création de la table `osir_handlers`: {e}")
            raise

    def create(self, case_uuid: str, modules: List[str], task_ids: List[str], handler_id: uuid.UUID = None) -> str:
        try:
            if not handler_id:
                handler_id = uuid.uuid4()
            self.db.cur.execute("""
                INSERT INTO osir_handlers (
                    handler_id,
                    case_uuid,
                    modules,
                    task_id,
                    processing_status
                )
                VALUES (%s, %s, %s, %s, 'processing_started')
            """, (handler_id, case_uuid, modules, task_ids))
            self.db.conn.commit()
            logger.debug(f"Handler créé avec succès avec handler_id: {handler_id}")
            return handler_id
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Erreur lors de la création du handler: {e}")
            raise

    def get(self, handler_id: Optional[str] = None, case_uuid: Optional[str] = None) -> Union[Dict, List[Dict], None]:
        try:
            if isinstance(case_uuid, str):
                case_uuid = uuid.UUID(case_uuid)
            if handler_id:
                self.db.cur.execute("""
                    SELECT * FROM osir_handlers
                    WHERE handler_id = %s::uuid
                """, (handler_id,))
            elif case_uuid:
                self.db.cur.execute("""
                    SELECT * FROM osir_handlers
                    WHERE case_uuid = %s
                """, (case_uuid,))
            else:
                raise ValueError("Soit un `handler_id`, soit un `case_uuid` doit être fourni.")

            rows = self.db.cur.fetchall()
            if not rows:
                # TODO : Change with class
                return {
                    "case_uuid": case_uuid,
                    "handler_id": handler_id,
                    "modules": None,
                    "task_ids": None,
                    "processing_status": None
                }

            if handler_id:
                return self._row_to_dict(rows[0])
            else:
                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des handlers: {e}")
            raise

    def _row_to_dict(self, row) -> Dict:
        return {
            "handler_id": str(row[0]),
            "case_uuid": row[1],
            "modules": row[2],
            "task_ids": row[3],
            "processing_status": row[4]
        }

    def update(self, handler_id: str, processing_status: str) -> bool:
        try:
            self.db.cur.execute("""
                UPDATE osir_handlers
                SET processing_status = %s
                WHERE handler_id = %s
            """, (processing_status, handler_id))
            self.db.conn.commit()
            logger.debug(f"Statut du handler {handler_id} mis à jour avec succès.")
            return True
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Erreur lors de la mise à jour du statut du handler {handler_id}: {e}")
            raise

    def append_task_ids(self, handler_id: str, new_task_ids: List[str]) -> bool:
        try:
            self.db.cur.execute("""
                SELECT task_id FROM osir_handlers WHERE handler_id = %s
            """, (handler_id,))
            result = self.db.cur.fetchone()
            if result is None:
                logger.error(f"Aucun handler trouvé avec l'ID {handler_id}.")
                return False

            current_task_ids = result[0] or []
            if isinstance(current_task_ids, str):
                current_task_ids = [current_task_ids]

            updated_task_ids = []
            for task_id in current_task_ids + new_task_ids:
                if isinstance(task_id, str):
                    task_id_uuid = uuid.UUID(task_id)
                    updated_task_ids.append(task_id_uuid)
                else:
                    updated_task_ids.append(task_id)

            updated_task_ids = list(set(updated_task_ids))

            self.db.cur.execute("""
                UPDATE osir_handlers
                SET task_id = %s
                WHERE handler_id = %s
            """, (updated_task_ids, handler_id))
            self.db.conn.commit()
            logger.debug(f"Liste des task_ids pour le handler {handler_id} mise à jour avec succès.")
            return True
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Erreur lors de la mise à jour des task_ids pour le handler {handler_id}: {e}")
            raise

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
    
    def list(
        self,
        case_uuid: Optional[str] = None,
        processing_status: Optional[Union[str, List[str]]] = None,
        exclude_status: Optional[Union[str, List[str]]] = None
    ) -> List[Dict]:
        try:
            # Jointure avec osir_case pour récupérer le nom du cas
            query = """
                SELECT h.*, c.name AS case_name
                FROM osir_handlers h
                LEFT JOIN osir_case c ON h.case_uuid = c.case_uuid
            """
            conditions = []
            params = []

            if case_uuid:
                # Vérifiez si case_uuid est déjà un objet UUID
                if isinstance(case_uuid, uuid.UUID):
                    uuid_value = case_uuid
                else:
                    uuid_value = uuid.UUID(case_uuid)
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

            self.db.cur.execute(query, params)
            rows = self.db.cur.fetchall()

            # Mise à jour de _row_to_dict pour inclure le nom du cas
            results = []
            for row in rows:
                row_dict = self._row_to_dict(row)
                # Ajouter le nom du cas (peut être None si non trouvé)
                row_dict["case_name"] = row[-1]  # Le dernier champ est case_name
                results.append(row_dict)

            return results
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la liste des handlers: {e}")
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
    
    def delete(self, handler_id: Optional[str] = None, case_uuid: Optional[str] = None) -> bool:
        """
        Supprime un ou plusieurs enregistrements de la table osir_handlers en utilisant soit le handler_id, soit le case_uuid.

        Args:
            handler_id (Optional[str]): L'ID du handler à supprimer.
            case_uuid (Optional[str]): L'UUID du cas dont les handlers doivent être supprimés.

        Returns:
            bool: True si la suppression a réussi, False sinon.
        """
        try:
            if not handler_id and not case_uuid:
                raise ValueError("Soit un `handler_id`, soit un `case_uuid` doit être fourni.")

            if handler_id:
                # Supprimer un handler spécifique
                self.db.cur.execute("""
                    DELETE FROM osir_handlers
                    WHERE handler_id = %s
                """, (handler_id,))
                logger.debug(f"Handler avec l'ID {handler_id} supprimé avec succès.")
            elif case_uuid:
                # Supprimer tous les handlers associés à un cas
                if isinstance(case_uuid, str):
                    case_uuid = uuid.UUID(case_uuid)
                self.db.cur.execute("""
                    DELETE FROM osir_handlers
                    WHERE case_uuid = %s
                """, (case_uuid,))
                logger.debug(f"Tous les handlers associés au cas {case_uuid} ont été supprimés avec succès.")

            self.db.conn.commit()
            return True
        except ValueError as ve:
            logger.error(f"Erreur de validation: {ve}")
            raise
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Erreur lors de la suppression du handler: {e}")
            raise
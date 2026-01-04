from typing import Union, List, Tuple
import uuid
from osir_lib.core.FileManager import FileManager
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

class CaseManager:
    def __init__(self, db_osir):
        self.db = db_osir

    def create_table(self):
        try:
            # Utilisation de 'with' pour le curseur
            with self.db.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS osir_case (
                        case_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name TEXT NOT NULL UNIQUE
                    )
                """)
            self.db.conn.commit()
        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Error creating table osir_case: {e}")
            raise

    def create(self, name: str) -> str:
        try:
            with self.db.conn:
                with self.db.conn.cursor() as cur:
                    # Vérifie si un case avec ce nom existe déjà
                    cur.execute("SELECT case_uuid FROM osir_case WHERE name = %s", (name,))
                    existing_case = cur.fetchone()

                    if existing_case:
                        # Retourne l'UUID du case existant
                        return str(existing_case[0])

                    # Si le case n'existe pas, le crée
                    case_uuid = str(uuid.uuid4())
                    cur.execute(
                        "INSERT INTO osir_case (case_uuid, name) VALUES (%s, %s)",
                        (case_uuid, name)
                    )
                    return case_uuid
        except Exception as e:
            logger.error(f"Erreur lors de la création du case '{name}': {e}")
            raise


    def get(self, case_uuid: str = None, name: str = None) -> Union[str, None]:
        try:
            with self.db.conn.cursor() as cur:
                if case_uuid:
                    cur.execute("SELECT case_uuid FROM osir_case WHERE case_uuid = %s::uuid", (case_uuid,))
                elif name:
                    cur.execute("SELECT case_uuid FROM osir_case WHERE name = %s", (name,))
                else:
                    raise ValueError("Soit un `case_uuid`, soit un `name` doit être fourni.")

                result = cur.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Error fetching case UUID: {e}")
            raise

    def list(self) -> List[Tuple[str, str]]:
        try:
            with self.db.conn.cursor() as cur:
                cur.execute("SELECT case_uuid, name FROM osir_case")
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Error listing cases: {e}")
            raise
    
    def delete(self, case_uuid: str) -> bool:
        """Supprime un case de la base de données."""
        try:
            with self.db.conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM osir_case WHERE case_uuid = %s
                """, (case_uuid,))            
            self.db.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting case: {e}")
            raise
    
    
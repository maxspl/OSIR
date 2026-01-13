from typing import Union, List, Tuple
import uuid
from osir_lib.core.FileManager import FileManager

from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()

class CaseManager:
    def __init__(self, db_osir):
        self.db = db_osir

    def create_table(self):
        try:
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS osir_case (
                    case_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name TEXT NOT NULL UNIQUE
                )
            """)
            
        except Exception as e:
            
            logger.error(f"Error creating table osir_case: {e}")
            raise

    def create(self, name: str) -> str:
        try:
            existing_case = self.db.execute_query("SELECT case_uuid FROM osir_case WHERE name = %s", (name,), fetch="fetchone")

            if existing_case:
                # Retourne l'UUID du case existant
                return str(existing_case[0])

            # Si le case n'existe pas, le crée
            case_uuid = str(uuid.uuid4())
            self.db.execute_query(
                "INSERT INTO osir_case (case_uuid, name) VALUES (%s, %s)",
                (case_uuid, name)
            )
            return case_uuid
        except Exception as e:
            logger.error(f"Erreur lors de la création du case '{name}': {e}")
            raise


    def get(self, case_uuid: str = None, name: str = None) -> Union[str, None]:
        try:
            if case_uuid:
                result = self.db.execute_query("SELECT case_uuid FROM osir_case WHERE case_uuid = %s::uuid", (case_uuid,), fetch="fetchone")
            elif name:
                result = self.db.execute_query("SELECT case_uuid FROM osir_case WHERE name = %s", (name,), fetch="fetchone")
            else:
                raise ValueError("Soit un `case_uuid`, soit un `name` doit être fourni.")

            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error fetching case UUID: {e}")
            raise

    def list(self) -> List[Tuple[str, str]]:
        try:
            return self.db.execute_query("SELECT case_uuid, name FROM osir_case", fetch="fetchall")
        except Exception as e:
            logger.error(f"Error listing cases: {e}")
            raise
    
    def delete(self, case_uuid: str) -> bool:
        """Supprime un case de la base de données."""
        try:
            self.db.execute_query("""
                DELETE FROM osir_case WHERE case_uuid = %s
            """, (case_uuid,))            
            
            return True
        except Exception as e:
            logger.error(f"Error deleting case: {e}")
            raise
    
    
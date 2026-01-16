from typing import Union, List, Tuple
import uuid
from osir_lib.core.FileManager import FileManager
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()


class CaseManager:
    """
        Manages the lifecycle of forensic cases within the PostgreSQL database.

        The CaseManager handles the creation, retrieval, and deletion of case 
        metadata.
    """

    def __init__(self, db_osir):
        """
            Initializes the CaseManager with an active database connection.

            Args:
                db_osir (DbOSIR): An instance of the OSIR database service.
        """
        self.db = db_osir

    def create_table(self):
        """
            Initializes the 'osir_case' table in the database if it does not exist.

            The table structure ensures that case names are unique to prevent 
            data collision between different investigations.
        """
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
        """
            Registers a new case in the database or retrieves an existing one.

            Args:
                name (str): The human-readable name of the forensic case.

            Returns:
                str: The UUID of the created or existing case.
        """
        try:
            existing_case = self.db.execute_query(
                "SELECT case_uuid FROM osir_case WHERE name = %s",
                (name,),
                fetch="fetchone"
            )

            if existing_case:
                # Return the existing case UUID if found
                return str(existing_case[0])

            # Generate a new unique identifier for the case
            case_uuid = str(uuid.uuid4())
            self.db.execute_query(
                "INSERT INTO osir_case (case_uuid, name) VALUES (%s, %s)",
                (case_uuid, name)
            )
            return case_uuid
        except Exception as e:
            logger.error(f"Error during creation of case '{name}': {e}")
            raise

    def get(self, case_uuid: str = None, name: str = None) -> Union[str, None]:
        """
            Retrieves a case UUID based on either the ID or the name.

            Args:
                case_uuid (str, optional): The UUID of the case.
                name (str, optional): The name of the case.

            Returns:
                Union[str, None]: The found UUID or None if no match is found.

            Raises:
                ValueError: If neither case_uuid nor name is provided.
        """
        try:
            if case_uuid:
                result = self.db.execute_query(
                    "SELECT case_uuid FROM osir_case WHERE case_uuid = %s::uuid",
                    (case_uuid,),
                    fetch="fetchone"
                )
            elif name:
                result = self.db.execute_query(
                    "SELECT case_uuid FROM osir_case WHERE name = %s",
                    (name,),
                    fetch="fetchone"
                )
            else:
                raise ValueError("Either 'case_uuid' or 'name' must be provided.")

            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error fetching case UUID: {e}")
            raise

    def list(self) -> List[Tuple[str, str]]:
        """
            Lists all forensic cases stored in the database.

            Returns:
                List[Tuple[str, str]]: A list of tuples containing (case_uuid, name).
        """
        try:
            return self.db.execute_query("SELECT case_uuid, name FROM osir_case", fetch="fetchall")
        except Exception as e:
            logger.error(f"Error listing cases: {e}")
            raise

    def delete(self, case_uuid: str) -> bool:
        """
            Removes a case record from the database.

            Args:
                case_uuid (str): The UUID of the case to remove.

            Returns:
                bool: True if the operation was successful.
        """
        try:
            self.db.execute_query("""
                DELETE FROM osir_case WHERE case_uuid = %s
            """, (case_uuid,))
            return True
        except Exception as e:
            logger.error(f"Error deleting case: {e}")
            raise

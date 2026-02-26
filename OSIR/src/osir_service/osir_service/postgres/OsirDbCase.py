from typing import Union, List, Tuple
import uuid
from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.logger import AppLogger
from osir_service.postgres.model.OsirDbCaseModel import OsirDbCaseModel

logger = AppLogger().get_logger()


class OsirDbCase:
    """
        Manages the lifecycle of forensic cases within the PostgreSQL database.

        The OsirDbCase handles the creation, retrieval, and deletion of case 
        metadata.
    """

    def __init__(self, db_osir):
        """
            Initializes the OsirDbCase with an active database connection.

            Args:
                db_osir (OsirDb): An instance of the OSIR database service.
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

    def create(self, name: str) -> OsirDbCaseModel:
        """
            Registers a new case in the database or retrieves an existing one.

            Args:
                name (str): The human-readable name of the forensic case.

            Returns:
                OsirDbCaseModel: The OsirDbCaseModel associated with the case.
        """
        try:
            existing_case = self.db.execute_query(
                "SELECT case_uuid, name FROM osir_case WHERE name = %s",
                (name,),
                fetch="fetchone"
            )

            if existing_case:
                # Return the existing case
                return OsirDbCaseModel.model_validate(existing_case)

            # Generate a new unique identifier for the case
            case_uuid = str(uuid.uuid4())
            self.db.execute_query(
                "INSERT INTO osir_case (case_uuid, name) VALUES (%s, %s)",
                (case_uuid, name)
            )
            FileManager.create_case(directory=OSIR_PATHS.CASES_DIR, case_name=name)
            return OsirDbCaseModel(case_uuid=case_uuid, name=name)
        except Exception as e:
            logger.error(f"Error during creation of case '{name}': {e}")
            raise

    def get(self, case_uuid: str = None, name: str = None) -> Union[OsirDbCaseModel, None]:
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
                    "SELECT * FROM osir_case WHERE case_uuid = %s::uuid",
                    (case_uuid,),
                    fetch="fetchone"
                )
            elif name:
                result = self.db.execute_query(
                    "SELECT * FROM osir_case WHERE name = %s",
                    (name,),
                    fetch="fetchone"
                )
            else:
                raise ValueError("Either 'case_uuid' or 'name' must be provided.")

            return OsirDbCaseModel.model_validate(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching case UUID: {e}")
            raise

    def list(self) -> List[OsirDbCaseModel]:
        """
            Lists all forensic cases stored in the database.

            Returns:
                List[OsirDbCaseModel]: A list of OsirDbCaseModel(case_uuid, name).
        """
        try:
            return [OsirDbCaseModel.model_validate(x) for x in self.db.execute_query("SELECT case_uuid, name FROM osir_case", fetch="fetchall")]
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

from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.LogUtils import LogUtils
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger, CustomLogger
from pathlib import Path
from dissect.database.sqlite3.sqlite3 import SQLite3

logger: CustomLogger = AppLogger().get_logger()
 

@osir_internal_module
class SqliteModule(LogUtils):
    """
    PyModule to perform processing operations on Audit logs.
    """

    def __init__(self, module: OsirModule):
        """
        Initializes the Module.

        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (OsirModule): Instance of OsirModule containing configuration details for the extraction process.
        """
        self.module = module
        LogUtils.__init__(self, ctx=module)
        self._file_to_process = module.input.match

    def __call__(self) -> bool:
        """
        Execute the internal processor of the module
        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        try:
            logger.debug(f"Processing Started: \n File Input: {self._file_to_process} \n")
    
            writer_queue = self.start_writer_thread()
    
            with SQLite3(Path(self._file_to_process)) as db:
                for table in db.tables():
                    logger.debug(f"Processing Table: {table.name}")
                    for row in table.rows():
                        record = dict(iter(row))
                        record["_table"] = table.name
                        writer_queue.put(record)
                    logger.debug(f"Table Done: {table.name}")
    
            writer_queue.put(None)
    
            logger.debug(f"Processing Done: \n File Input: {self._file_to_process} \n")
    
        except Exception as exc:
            logger.error_handler(exc)
            return False
    
        return True
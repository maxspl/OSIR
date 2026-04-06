from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.LogUtils import LogUtils
from osir_lib.core.OsirModule import OsirModule, Path
from osir_lib.logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()

@osir_internal_module
class ZeekConnModule(LogUtils):
    """
    PyModule to perform processing operations on Zeek conn.log.
    """

    def __init__(self, module: OsirModule):
        """
        Initializes the Module.

        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (OsirModule): Instance of OsirModule containing configuration details for the extraction process.
        """
        self.module = module
        self._file_to_process = module.input.match

    def __call__(self) -> bool:
        """
        Execute the internal processor of the module.

        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        try:
            logger.debug(f"Processing file {self._file_to_process}")

            from zat.log_to_dataframe import LogToDataFrame

            input_path  = Path(self.module.input.match)
            df = LogToDataFrame().create_dataframe(str(input_path))
            df.to_json(self.module.output.output_file, orient="records", lines=True)

            logger.debug(f"{self.module.module_name} done")
            return True
        except Exception as exc:
            logger.error_handler(exc)
            return False
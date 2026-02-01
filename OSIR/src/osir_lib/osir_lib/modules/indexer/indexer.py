import re
import os
import copy
from datetime import datetime
from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


@osir_internal_module
class InjectionModule():
    """
    PyModule to inject log into Splunk.
    """

    def __init__(self, module: OsirModule):
        """
        Initializes the Module.

        Args:
            module (OsirModule): Instance of OsirModule containing configuration details for the extraction process.
        """
        self.module = module
        self._dir_to_process = module.input.match

    def __call__(self) -> bool:
        """
        Execute the internal processor of the module.

        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        try:
            logger.debug(f"Processing file {self._dir_to_process}")
            for module_dir_name in os.listdir(self._dir_to_process):
                if os.path.isdir(os.path.join(self._dir_to_process, module_dir_name)):
                    try:
                        child_module_model = OsirModuleModel.from_name(module_dir_name)
                    except FileNotFoundError:
                        logger.warning(f"Skipping directory '{module_dir_name}' — no matching module found.")
                        continue  # Skip to next directory
                    if child_module_model:
                        logger.debug(f"Module found {module_dir_name}")

                        # Dump model to add mandatory fields before validation : case_path and match
                        child_module_data = child_module_model.model_dump()
                        child_module_data["case_path"] = self.module.case_path
                        child_module_data["input"]["match"] = os.path.join(self._dir_to_process, module_dir_name)

                        # Transform model to instance. Mandatory to get _module_filepath
                        child_module_instance = OsirModule.model_validate(child_module_data)

                        replacements = {
                            "indexer_path": child_module_instance._module_filepath
                        }
                        self.module.tool.cmd = self.module.tool.safe_format(self.module.tool.cmd, **replacements)

                        # Run json2splunk is splunk configuration exists
                        splunk_indexer_data = child_module_instance.splunk
                        if splunk_indexer_data:
                            self.module.tool.run()
                    else:
                        logger.warning(f"Module not found {module_dir_name}")

            logger.debug(f"{self.module.module_name} done")

        except Exception as exc:
            logger.error_handler(exc)


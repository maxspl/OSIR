from osir_lib.core.FileManager import FileManager
from osir_lib.core.model.OsirProfileModel import OsirProfileModel
from osir_lib.core.OsirModule import OsirModule

from osir_lib.core.AgentConfig import AgentConfig
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

class OsirProfile(OsirProfileModel):
    modules_instance: list[OsirModule] = None

    def __init__(self, **data):
        super().__init__(**data)

        # -------- AUTO-CONVERSIONS OF NESTED MODELS -------- #
        
        if self.modules : 
            self.modules_instance: list[OsirModule] = [OsirModule.from_yaml(FileManager.get_module_path(module)) for module in self.modules]

    def _validate_modules_configs(self):
        """
        Validates the configurations of all selected modules, checking their existence, operating system compatibility, and requirements.
        
        Raises:
            SystemExit: If any validation checks fail, indicating critical errors in module configuration.
        """
        # Validate os
        os_values = set()
        for module_instance in self.module_instances:
            os_values.add(module_instance.get_os())

        if len(os_values) == 1 or "all" in os_values:
            logger.debug("All module instances have the same OS.")
        else:
            logger.error("Modules instances have different OS. Please check configuration.")       
            exit()
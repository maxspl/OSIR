import os
import uuid
from src.utils import BaseModule
from .ModuleHandler import ModuleHandler
from src.log.logger_config import AppLogger
from threading import Thread, Event
from src.utils import DbOSIR

logger = AppLogger(__name__).get_logger()


class MonitorCase:
    """
    Monitors a specified case path for changes that trigger module actions based on the defined module configurations.
    """
    def __init__(self, case_path, modules, reprocess_case):
        """
        Initializes the monitoring setup with the specified case path and modules.

        Args:
            case_path (str): The path to the directory to be monitored.
            modules (list): List of modules to apply to the monitoring events.
            reprocess_case (bool): If True, it will reprocess all the files. If False, files that were present during previous execution will not be processed.
        """
        self.case_path = case_path
        self.modules = modules
        self.reprocess_case = reprocess_case
        
        self.module_instances = [BaseModule.BaseModule(module) for module in modules]  # Transform list of str to list of module
        self.cooldown_period = 20  # Cooldown period in seconds 
        self.case_uuid = self._generate_unique_id(os.path.basename(self.case_path))
        
        self.stop_event = Event()
        
        self.db_OSIR = DbOSIR.DbOSIR("postgres", module_name="master_status")  # Use docker service name
        self.db_OSIR.store_master_status(case_path, "processing_case", self.case_uuid, self.modules)

    def on_inactivity(self):
        """Method to be called when inactivity is detected."""
        self.db_OSIR.store_master_status(self.case_path, "processing_done", self.case_uuid, self.modules)
        logger.debug("Updated database status to processing_done due to inactivity.")
        
    def _generate_unique_id(self, prefix: str):
        """
        Generates a unique identifier prefixed with a specific string.

        Args:
            prefix (str): Prefix for the unique identifier.

        Returns:
            str: The prefixed unique identifier.
        """
        # Generate a random UUID
        unique_id = uuid.uuid4()
        # Prefix the UUID with the given string
        prefixed_id = f"{prefix}-{unique_id}"
        return prefixed_id

    def setup_handler(self):
        """
        Sets up file and directory event handlers for each module, configuring and starting an observer to monitor the filesystem.
        """
        modules_info = []
        for module_instance in self.module_instances:
            module_name = module_instance.module_name
            file_regex = module_instance.input.name

            if module_instance.input.path:
                path_pattern = module_instance.input.path.rstrip('/')
            else:
                path_pattern = None  # No path criteria given

            if not module_instance.input.type:
                logger.error("type is missing in module configuration")
                exit()  # To change
            else:
                input_type = module_instance.input.type

            module_info = {
                "module_name": module_name,
                "file_regex": file_regex,
                "path_pattern_suffix": path_pattern,
                "input_type": input_type
            }
            modules_info.append(module_info)
            
        handler = ModuleHandler(self.case_path, modules_info, self.cooldown_period, self.module_instances, self.case_uuid)
        monitor_case_thread = Thread(target=handler.monitor_directory, args=(self.case_path, 10, self.reprocess_case))
        monitor_case_thread.start()
        monitor_case_thread.join()
        self.on_inactivity()


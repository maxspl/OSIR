import os
from pathlib import Path
import uuid

from threading import Thread, Event

import concurrent
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_lib.logger import AppLogger
from osir_lib.logger.logger import CustomLogger
from osir_service.postgres.OsirDb import OsirDb
from osir_service.watchdog.WatchdogService import ModuleHandler

logger: CustomLogger = AppLogger(__name__).get_logger()


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
        self.handler_uuid = uuid.uuid4()
        self.case_path = case_path
        self.modules = modules
        self.reprocess_case = reprocess_case

        self.module_instances = [OsirModuleModel.from_name(module) for module in modules]  # Transform list of str to list of module
        self.cooldown_period = 20  # Cooldown period in seconds
        case_name = os.path.basename(self.case_path)
        with OsirDb() as db:
            case = db.case.get(name=case_name)
            if not case:
                self.case_uuid = db.case.create(case_name).case_uuid
            else:
                self.case_uuid = case.case_uuid
        self.stop_event = Event()

    def on_inactivity(self):
        """Method to be called when inactivity is detected."""
        logger.debug("Updated Handler status to processing_done due to inactivity.")

    def setup_handler(self):
        """
        Sets up file and directory event handlers for each module, configuring and starting an observer to monitor the filesystem.
        """
        try:
            handler = ModuleHandler(Path(self.case_path), self.cooldown_period, self.module_instances, self.case_uuid, self.handler_uuid)
            monitor_case_thread = Thread(target=handler.monitor_directory, args=(self.case_path, 10, self.reprocess_case))
            monitor_case_thread.start()
            monitor_case_thread.join()
            self.on_inactivity()
        except Exception as e:
            logger.error_handler(e)

    def start(self):
        try:
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            executor.submit(self.setup_handler)
        except Exception as e:
            logger.error_handler(e)
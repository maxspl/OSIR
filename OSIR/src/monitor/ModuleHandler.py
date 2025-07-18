import re
import time
import os
from threading import Timer
import threading  # Import threading to use Lock
import pkgutil
import importlib
import pickle
import copy
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from src.log.logger_config import AppLogger
from src.tasks import task_client
from src.utils.DbOSIR import DbOSIR
from src.utils.PyModule import PyModule
from src.utils.AgentConfig import AgentConfig
from watchdog.events import DirCreatedEvent, FileCreatedEvent


logger = AppLogger(__name__).get_logger()


class CaseSnapshot:
    """
    Class to snapshot the directory entries.
    """
    def __init__(self, case_path):
        """
        Initialize the CaseSnapshot with the given case path.

        Args:
            case_path (str): The path of the case to snapshot.
        """
        self.case_path = case_path
        self.entries = []

    def scan_directory(self):
        """
        Scan the directory and subdirectories to record entries.
        """
        self.entries = []  # Reset entries before scanning
        
        def scan(current_path):
            with os.scandir(current_path) as it:
                for entry in it:
                    if entry.is_dir():
                        self.entries.append((entry.path, 'directory'))
                        scan(entry.path)  # Recursively scan subdirectory
                    elif entry.is_file():
                        self.entries.append((entry.path, 'file'))
        
        scan(self.case_path)
        # Add case_path
        self.entries.append((self.case_path, 'directory'))
    
    def get_entries_set(self):
        """
        Get a set of the directory entries for easy comparison.

        Returns:
            set: A set of tuples representing the entries.
        """
        # Return a set of entries for easy comparison
        return set(self.entries)
    

class ModuleHandler(FileSystemEventHandler):
    """
    Handles file system events to trigger processing modules based on file or directory changes that match specified patterns.
    """
    def __init__(self, case_path, modules_info, cooldown_period, module_instances, case_uuid):
        """
        Initializes the ModuleHandler with configurations to monitor file and directory events related to a specific case.

        Args:
            case_path (str): Base path on master's disk of the case to monitor.
            modules_info (list): List of module information dicts.
            cooldown_period (int): Cooldown period between checks in seconds.
            module_instances (list): List of module instances to execute.
            case_uuid (str): Unique identifier for the case.
        """

        self.modules_info = modules_info
        self.cooldown = cooldown_period
        self.watch_directory = case_path
        self.case_path = case_path
        self.last_modified_times = {}
        self.module_instances = module_instances
        self.case_uuid = case_uuid
        
        self.last_size = {}
        self.last_processed = set()

        self.agent_config = AgentConfig()
        if self.agent_config.standalone:
            db_postgres = "master-postgres"
        else:
            db_postgres = self.agent_config.master_host
        
        # Initialize a set and a lock to keep track of active timers
        self.active_timers = set()
        self.timers_lock = threading.Lock()
        
        # DB management
        self.DbOSIR = DbOSIR(db_postgres)

        # Create tables for each
        for module_info in self.modules_info:
            module_name = module_info["module_name"]
            self.DbOSIR.create_table_processing_status(module_name)

    def monitor_directory(self, case_path, interval=5, reprocess=False):
        """
        Monitors the directory for changes at specified intervals.

        Args:
            case_path (str): Path of the case to monitor.
            interval (int, optional): Interval in seconds to wait between scans. Default is 5 seconds.
            reprocess (bool): If True, it will reprocess all the files. If False, files that were present during previous execution will not be processed.
        """
        casesnapshot = CaseSnapshot(case_path)
        
        if not reprocess:
            # Fetch previously stored entries
            logger.debug(f"Fetching previously stored entries for case_uuid={self.case_uuid}")
            previous_entries = set(self.DbOSIR.get_stored_case_snapshot(case_path))
            if not previous_entries:
                logger.debug("No previous entries found, starting with an empty set.")
        else:
            previous_entries = set()

        while True:
            logger.debug("Scanning for new files/folders")
            scan_case_start_time = time.time()
            casesnapshot.scan_directory()
            current_entries = casesnapshot.get_entries_set()
            scan_case_end_time = time.time()
            scan_case_duration = scan_case_end_time - scan_case_start_time
            logger.debug(f"Time taken to scan case: {scan_case_duration:.4} seconds.")
            new_entries = current_entries - previous_entries
            if new_entries:
                new_entries_start_time = time.time()
                logger.debug(f"New files/folders detected : {len(new_entries)} new items")
                for entry in new_entries:
                    item_path, entry_type = entry
                    if entry_type == 'file':
                        self.on_created(FileCreatedEvent(item_path))
                    elif entry_type == 'directory':
                        self.on_created(DirCreatedEvent(item_path))

                new_entries_end_time = time.time()
                new_entries_duration = new_entries_end_time - new_entries_start_time
                logger.debug(f"Time taken to process new items: {new_entries_duration:.4} seconds")
            else:
                logger.debug("No new item detected. Checking if a task is still ongoing before exiting...")
                if not self.DbOSIR.is_processing_active(self.case_uuid):
                    with self.timers_lock:
                        if not self.active_timers:
                            logger.debug("Case snaphost is being saved before exiting...")
                            self.DbOSIR.store_case_snapshot(self.case_uuid, case_path, list(current_entries))
                            exit()
            previous_entries = current_entries
            
            time.sleep(interval)
    
    def on_created(self, event):  # triggered for files and dir but targets dirs only
        """
        Specific handler for 'created' events, which are triggered when a new file or directory is created.

        Args:
            event: The event object representing the file or directory creation event.
        """
        for module_info in self.modules_info:
            file_regex = re.compile(module_info["file_regex"])
            path_pattern_suffix = module_info["path_pattern_suffix"]
            if path_pattern_suffix:
                wildcard_pattern = path_pattern_suffix.rstrip('/*')  # Wildcard can be used after suffix to match any directory (not recursive)
            module_name = module_info["module_name"]
            input_type = module_info["input_type"]
            module_path = os.path.join(self.case_path, module_name)
            # Create a tuple of (file_path, module_name)
            file_module_pair = (event.src_path, module_name)

            # Check if path_pattern_suffix is a regex
            is_path_pattern_suffix_regex = path_pattern_suffix.startswith("r\"") and path_pattern_suffix.endswith("\"") if path_pattern_suffix else None
            if is_path_pattern_suffix_regex:
                # Strip r"" and compile the regex
                path_regex = re.compile(path_pattern_suffix[2:-1])
            else:
                wildcard_pattern = path_pattern_suffix.rstrip('/*') if path_pattern_suffix else None  # Wildcard can be used after suffix to match any directory (not recursive)

            # Handle dirs
            if (module_path not in event.src_path and  # don't process input if it is in the same module directory
                    input_type == "dir" and
                    event.is_directory):  
                
                if is_path_pattern_suffix_regex and path_regex.search(event.src_path):  # Regex match for directories
                    logger.debug(f"{module_name} Directory '{event.src_path}' will be processed (regex match)")
                    self.handle_directory_event(event, module_info)
                # Handle case where input dir is case directory
                elif (path_pattern_suffix == "{case_path}" and
                        event.src_path == self.case_path):
                    logger.debug(f"{module_name} Directory '{event.src_path}' will be processed")
                    self.handle_directory_event(event, module_info)
                elif ("{case_path}" in path_pattern_suffix and event.src_path == path_pattern_suffix.replace("{case_path}", self.case_path)):
                    logger.debug(f"{module_name} Directory '{event.src_path}' will be processed")
                    self.handle_directory_event(event, module_info)
                elif path_pattern_suffix.endswith('/*') and os.path.dirname(event.src_path).lower().endswith(wildcard_pattern.lower()):
                    logger.debug(f"{module_name} Directory '{event.src_path}' will be processed")
                    self.handle_directory_event(event, module_info)
                elif event.src_path.lower().endswith(path_pattern_suffix.lower()):
                    logger.debug(f"{module_name} Directory '{event.src_path}' will be processed")
                    self.handle_directory_event(event, module_info)

            # Handle files
            elif (module_path not in os.path.dirname(event.src_path) and  # don't process input if it is in the same module directory
                    input_type == "file" and
                    not event.is_directory and
                    file_module_pair not in self.last_processed):
                
                if is_path_pattern_suffix_regex and path_regex.search(event.src_path):  # Regex match for files
                    if re.search(file_regex, os.path.basename(event.src_path)):
                        self.last_processed.add(file_module_pair)
                        self.handle_file_event(event, module_info)
                elif path_pattern_suffix and not file_regex.pattern:  # If only path specified, the event file must end with the path in config
                    if event.src_path.lower().endswith(path_pattern_suffix.lower()):
                        self.last_processed.add(file_module_pair)
                        self.handle_file_event(event, module_info)
                # NEED A REVIEW OF THIS ADD !!!!!!!!
                elif path_pattern_suffix and '/*' in path_pattern_suffix and path_pattern_suffix.replace('/*', '') in event.src_path.lower() and re.search(file_regex, os.path.basename(event.src_path)):
                    self.last_processed.add(file_module_pair)
                    self.handle_file_event(event, module_info)

                elif path_pattern_suffix and file_regex.pattern:  # If path/file name both specified, the directory of the event file must end with the path in config
                    if os.path.dirname(event.src_path).lower().endswith(path_pattern_suffix.lower()) and re.search(file_regex, os.path.basename(event.src_path)):
                        self.last_processed.add(file_module_pair)
                        self.handle_file_event(event, module_info)
                elif not path_pattern_suffix and file_regex.pattern:  # If on_close triggered, the filename regex already matched
                    if re.search(file_regex, os.path.basename(event.src_path)):  
                        self.last_processed.add(file_module_pair)
                        self.handle_file_event(event, module_info)

    def handle_file_event(self, event, module_info):
        """
        Processes file events that match configured patterns.

        Args:
            event: The event object representing the file event.
            module_info (dict): Dictionary containing module information.
        """
        module_name = module_info["module_name"]
        logger.debug(f"{module_name}.yaml - File Matched : {event.src_path}")
        self.process_file(event.src_path, module_info)

    def handle_directory_event(self, event, module_info):
        """
        Processes directory events that match configured patterns and sets up checks for idleness.

        Args:
            event: The event object representing the directory event.
            module_info (dict): Dictionary containing module information.
        """
        module_name = module_info["module_name"]
        current_time = time.time()
        self.last_modified_times[event.src_path] = current_time
        
        # Check directory size immediately and store it
        current_size = self._get_directory_size(event.src_path)
        self.last_size[event.src_path] = current_size
        
        # Start a new timer to check for idleness
        timer = Timer(self.cooldown, self._check_for_idle, [event.src_path, module_info])
        try:
            logger.debug(f"{module_name} Starting timer for IDLE check of '{event.src_path}'")
            with self.timers_lock:
                self.active_timers.add(event.src_path)
            timer.start()
            logger.debug(f"{module_name} Timer started for IDLE check of '{event.src_path}'")
        except Exception as e:
            logger.debug(f"{module_name} Timer error for {event.src_path}. {str(e)}")
        logger.debug(f"{module_name} Directory '{event.src_path}' is busy")
    
    def _get_directory_size(self, path):
        """
        Calculates the total size of files within a specified directory.

        Args:
            path (str): Path to the directory.

        Returns:
            int: Total size of all files within the directory.
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def _check_parent(self, path, module_info):
        module_name = module_info["module_name"]

        logger.debug(f"Checking if {module_name} idle is not parent of another idle")

        # Convert path to a Path object
        path = Path(path).resolve()

        for current_idle_path in list(self.active_timers):
            current_idle_path_resolved = Path(current_idle_path).resolve()

            # Check if the current path is a parent of the active timer path
            if current_idle_path_resolved.is_relative_to(path) and path != current_idle_path_resolved:
                logger.debug(f"{module_name} is parent of {current_idle_path}, the module can't be executed")
                return False

        return True
    
    def _check_for_idle(self, path, module_info):
        """
        Checks if the directory has been idle based on size changes and triggers further processing if idle.

        Args:
            path (str): Path to the directory being monitored.
            module_info (dict): Dictionary containing module information.
        """
        logger.debug(f"Starting _check_for_idle for {path} - {module_info['module_name']}")
        module_name = module_info["module_name"]
        current_size = self._get_directory_size(path)
        previous_size = self.last_size.get(path, 0)
        
        if current_size == previous_size and self._check_parent(path, module_info):
            logger.debug(f"{module_name} Directory '{path}' is now idle")
            self.process_directory(path, module_info)
            with self.timers_lock:
                if path in self.active_timers:
                    self.active_timers.remove(path)
        else:
            logger.debug(f"{module_name} Directory '{path}' is still busy, rescheduling check")
            # Reschedule the check if the directory size has changed
            self.last_size[path] = current_size
            timer = Timer(self.cooldown, self._check_for_idle, [path, module_info])
            timer.start()

    def process_file(self, file_path, module_info):
        """
        Initiates processing of a file based on the module configuration.

        Args:
            file_path (str): Path to the file to be processed.
            module_info (dict): Dictionary containing module information.
        """
        
        module_name = module_info["module_name"]
        logger.debug(f"Nom trouvé : {module_name}")

        module_instance = self._get_module_instance(module_name)
        self._set_input(file_path, "file", module_instance)
        logger.debug(f"""{module_name}.yaml - Processing : \n
                    Case Path : {self.case_path} \n
                    File Input: {file_path.split(self.case_path)[-1]} \n""")
        processor_type = module_instance.get_processor_type()
        self.DbOSIR.store_data(self.case_path, module_instance, "task_created", self.case_uuid)
        if "internal" in processor_type:
            if self.module_exists(module_instance.module_name):
                # logger.debug(f"Executing internal module {module_instance.module_name}.py")
                self._push_task(module_instance)
            else:
                logger.error(f"Module missing {module_instance.module_name}")
        else:
            logger.debug(f"run external processor for {module_instance.module_name}")
            self._push_task(module_instance)
        
    def process_directory(self, directory_path, module_info):
        """
        Initiates processing of a directory based on the module configuration.

        Args:
            directory_path (str): Path to the directory to be processed.
            module_info (dict): Dictionary containing module information.
        """
        module_name = module_info["module_name"]
        module_instance = self._get_module_instance(module_name)
        
        # Create a deep copy for this thread/task
        module_instance = copy.deepcopy(module_instance)

        self._set_input(directory_path, "dir", module_instance)

        logger.debug(f"\n{module_name} Processing the directory: {directory_path}")
        
        module_instance.input.dir = directory_path  # MSP maybe useless because of _set_input
        
        processor_type = module_instance.get_processor_type()
        self.DbOSIR.store_data(self.case_path, module_instance, "task_created", self.case_uuid)
        if "internal" in processor_type:
            if self.module_exists(module_instance.module_name):
                logger.debug(f"run internal processor for {module_instance.module_name}")
                self._push_task(module_instance)
            else:
                logger.debug(f"Module missing {module_instance.module_name} to process input : {directory_path}")
            # self._push_task(module_instance)
        else:
            logger.debug(f"Pushing task for {module_name} to process {directory_path} - {module_instance.input.dir}")
            self._push_task(module_instance)
                
    def _set_input(self, input_path, input_type, module_instance):
        """
        Sets the input parameters for the module instance based on the type and path of the input.

        Args:
            input_path (str): Path to the input (file or directory).
            input_type (str): Type of the input ('file' or 'dir').
            module_instance: The module instance to set the input for.
        """
        if input_type == "file":
            module_instance.input.file = input_path
        elif input_type == 'dir':
            module_instance.input.dir = input_path

    def _push_task(self, module_instance):
        """
        Pushes a task to the task queue for processing based on the current module configuration.

        Args:
            module_instance: The module instance to be processed.
        """

        disk_only = module_instance.get_disk_only()
        no_multithread = module_instance.get_no_multithread()
        processor_type = module_instance.get_processor_type()
        processor_os = module_instance.get_processor_os()
        if "internal" in processor_type:
            task_name = "internal_processor_task"
            logger.debug(f"Pushing the internal task '{module_instance.module_name}.py' to Celery ")
        else:
            task_name = "external_processor_task"

        if disk_only and no_multithread:
            queue_name = f"{processor_os}_no_multithread_disk_only"
        elif disk_only:
            queue_name = f"{processor_os}_multithread_disk_only"
        elif no_multithread:
            queue_name = f"{processor_os}_no_multithread"
        else:
            queue_name = f"{processor_os}_multithread"

        # Collect task parameters
        task_params = (PyModule.remove_prefix(self.case_path), pickle.dumps(module_instance), task_name, queue_name, self.case_uuid)
        task_client.run_task(*task_params)

    @staticmethod
    def module_exists(module_name):
        """
        Verifies if a specific module exists within the defined module directory.

        Args:
            module_name (str): Name of the module to check.

        Returns:
            bool: True if the module exists, False otherwise.
        """ 

        directory = os.path.dirname(__file__)  # Gets the directory of the current script
        relative_path = os.path.join(directory, '..')
        absolute_path = os.path.abspath(relative_path)  # Converts to absolute path
        modules_directory = os.path.join(absolute_path, 'modules')

        # Base import path for modules
        base_path = 'src.modules.'
        
        # Walk through each directory and sub-directory in the 'modules' directory
        for _, name, is_pkg in pkgutil.walk_packages([modules_directory], base_path):
            if not is_pkg:
                try:
                    module = importlib.import_module(name)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, PyModule) and attr is not PyModule:
                            if name.split('.')[-1] == module_name:
                                logger.debug(f"PyModule Found : {module_name}.py")
                                return True

                except ImportError as e:
                    logger.debug(f"Failed to import {name}: {e}")
                    return False

    def _get_module_instance(self, module_name):
        """
        Retrieves the module instance by name.

        Args:
            module_name (str): The name of the module.

        Returns:
            The module instance if found, None otherwise.
        """
        for instance in self.module_instances:
            if instance.module_name == module_name:
                return instance
        return None

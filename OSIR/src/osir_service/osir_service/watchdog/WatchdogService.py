import re
import time
import os
import threading
import copy

from pathlib import Path
from threading import Timer
import uuid

from osir_lib.core.OsirUtils import normalize_osir_path
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from watchdog.events import DirCreatedEvent, FileCreatedEvent
from watchdog.events import FileSystemEventHandler
from osir_lib.core.OsirUtils import remove_placeholders
from osir_lib.core.OsirAgentConfig import OsirAgentConfig
from osir_service.orchestration.TaskService import TaskService
from osir_service.postgres.OsirDb import OsirDb
from osir_lib.logger import AppLogger

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
                    try:
                        if entry.is_dir():
                            self.entries.append((entry.path, 'directory'))
                            scan(entry.path)  # Recursively scan subdirectory
                        elif entry.is_file():
                            self.entries.append((entry.path, 'file'))
                    except OSError as e:
                        logger.warning(f"Unreadable entries : {entry}. Error: {str(e)}")
                        continue
                    
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

    def __init__(self, case_path: Path, cooldown_period: int, module_instances: list[OsirModuleModel], case_uuid, handler_uuid=None):
        """
        Initializes the ModuleHandler with configurations to monitor file and directory events related to a specific case.

        Args:
            case_path (str): Base path on master's disk of the case to monitor.
            modules_info (list): List of module information dicts.
            cooldown_period (int): Cooldown period between checks in seconds.
            module_instances (list): List of module instances to execute.
            case_uuid (str): Unique identifier for the case.
        """
        self.handler_uuid = handler_uuid if handler_uuid else uuid.uuid4()
        self.cooldown = cooldown_period
        self.watch_directory = case_path
        self.case_path = case_path
        self.last_modified_times = {}
        self.module_instances: list[OsirModuleModel] = module_instances
        self.case_uuid = case_uuid

        self.last_size = {}
        self.last_processed = set()

        self.agent_config = OsirAgentConfig()

        # Initialize a set and a lock to keep track of active timers
        self.active_timers = set()
        self.timers_lock = threading.Lock()
        with OsirDb() as db:
            db.handler.create(
                handler_id=self.handler_uuid,
                case_uuid=self.case_uuid,
                modules=[module.module_name for module in module_instances],
                task_ids=[]
            )

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
            with OsirDb() as db:
                previous_entries = set(db.snapshot.get_stored_case_snapshot(case_path))
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
                with OsirDb() as db:
                    if not db.handler.is_processing_active(self.handler_uuid):
                        with self.timers_lock:
                            if not self.active_timers:
                                logger.debug("Case snaphost is being saved before exiting...")
                                db.snapshot.store_case_snapshot(self.case_uuid, case_path, list(current_entries))
                                if db.handler.check_handler_failure(self.handler_uuid):
                                    db.handler.update(self.handler_uuid, "processing_failed")
                                else:
                                    db.handler.update(self.handler_uuid, "processing_done")
                                exit()
            previous_entries = current_entries

            time.sleep(interval)

    def check_match(self, src_path, pattern, module_name):
        src_path_obj = Path(src_path)
        src_path_str = str(src_path_obj)

        is_regex = False
        clean_pattern = pattern

        if pattern.startswith(('r"', "r'")):
            is_regex = True
            clean_pattern = pattern[2:-1]
        elif any(c in pattern for c in ['^', '$', '(', '|']):
            is_regex = True

        if is_regex:
            if re.search(clean_pattern, src_path_str):
                logger.info(f"MATCH [Regex] : {src_path_str} avec {pattern} (Module: {module_name})")
                return True
        else:
            if src_path_obj.match(pattern):
                logger.info(f"MATCH [Glob] : {src_path_str} avec {pattern} (Module: {module_name})")
                return True

        return False

    def on_created_new(self, event, module: OsirModuleModel):
        """
            Handles the creation of new files or directories by checking them against 
            module-specific filtering rules before triggering processing.

            Args:
                event (watchdog.events.FileSystemEvent): The event object representing 
                    the file system change.
                module (OsirModuleModel): The module configuration containing input 
                    types, patterns, and processing logic.

            Returns:
                None: This method performs actions (logging, triggering processing) 
                    but does not return a value.
        """
        if not hasattr(event, 'src_path'):
            logger.warning("Événement sans chemin source, ignoré.")
            return

        src_path = Path(event.src_path)

        if event.is_directory and module.input.type != "dir":
            return

        if not event.is_directory and module.input.type != "file":
            return

        output_dir = Path(self.case_path) / module.module_name
        event_path = Path(event.src_path).resolve()

        if output_dir in event_path.parents or event_path == output_dir:
            return
        
        if module.output.output_dir and '{case_path}' in module.output.output_dir:
            alt_output_dir = Path(remove_placeholders(module.output.output_dir.replace('{case_path}', str(self.case_path))))
            if alt_output_dir in event_path.parents or event_path == alt_output_dir:
                return

        # Only process FS folder in mounted disk
        virtual_dir = Path(self.case_path) / 'virtual'
        if virtual_dir in event_path.parents:
            if '/fs/' not in str(event_path):
                return

        file_module_pair = (event.src_path, module.module_name)

        if file_module_pair in self.last_processed:
            return

        if not hasattr(module.input, 'paths') or not module.input.paths:
            logger.debug(f"Aucun motif de chemin défini pour le module {module.__class__.__name__}, ignoré.")
            return

        for pattern in module.input.paths:

            if "{case_path}" in pattern:
                pattern = pattern.replace("{case_path}", self.case_path)

            if self.check_match(src_path, pattern, module.__class__.__name__):
                self.last_processed.add(file_module_pair)
                logger.warning(self.last_processed)
                if module.input.type == "dir":
                    self.handle_directory_event(event, module)
                elif module.input.type == "file":
                    self.process(event.src_path, module)

                break

    def on_created(self, event):  # triggered for files and dir but targets dirs only
        """
        Specific handler for 'created' events, which are triggered when a new file or directory is created.

        Args:
            event: The event object representing the file or directory creation event.
        """
        for module_instance in self.module_instances:
            # TODO: Test this with a full profile
            if hasattr(module_instance.input, 'paths') and module_instance.input.paths:
                self.on_created_new(event, module_instance)
            # TODO: Remove this LEGACY
            else:
                if module_instance.input.path:
                    path_pattern = module_instance.input.path.rstrip('/')
                else:
                    path_pattern = None  # No path criteria given

                module_info = {
                    "module_name": module_instance.module_name,
                    "file_regex": module_instance.input.name,
                    "path_pattern_suffix": path_pattern,
                    "input_type": module_instance.input.type
                }
                if module_info["file_regex"]:
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
                if (str(module_path) not in str(event.src_path) and  # don't process input if it is in the same module directory
                        input_type == "dir" and
                        event.is_directory):

                    if is_path_pattern_suffix_regex and path_regex.search(str(event.src_path)):  # Regex match for directories
                        logger.debug(f"{module_name} Directory '{event.src_path}' will be processed (regex match)")
                        self.handle_directory_event(event, module_instance)
                    # Handle case where input dir is case directory
                    elif (path_pattern_suffix == "{case_path}" and
                            str(event.src_path) == str(self.case_path)):
                        logger.debug(f"{module_name} Directory '{event.src_path}' will be processed")
                        self.handle_directory_event(event, module_instance)
                    elif ("{case_path}" in path_pattern_suffix and event.src_path == path_pattern_suffix.replace("{case_path}", str(self.case_path))):
                        logger.debug(f"{module_name} Directory '{event.src_path}' will be processed")
                        self.handle_directory_event(event, module_instance)
                    elif path_pattern_suffix.endswith('/*') and os.path.dirname(event.src_path).lower().endswith(wildcard_pattern.lower()):
                        logger.debug(f"{module_name} Directory '{event.src_path}' will be processed")
                        self.handle_directory_event(event, module_instance)
                    elif str(event.src_path).lower().endswith(path_pattern_suffix.lower()):
                        logger.debug(f"{module_name} Directory '{event.src_path}' will be processed")
                        self.handle_directory_event(event, module_instance)

                # Handle files
                elif (str(module_path) not in str(os.path.dirname(event.src_path)) and  # don't process input if it is in the same module directory
                        input_type == "file" and
                        not event.is_directory and
                        file_module_pair not in self.last_processed):

                    if is_path_pattern_suffix_regex and path_regex.search(event.src_path):  # Regex match for files
                        if re.search(file_regex, os.path.basename(event.src_path)):
                            self.last_processed.add(file_module_pair)
                            self.process(event.src_path, module_instance)
                    elif path_pattern_suffix and not file_regex.pattern:  # If only path specified, the event file must end with the path in config
                        if event.src_path.lower().endswith(path_pattern_suffix.lower()):
                            self.last_processed.add(file_module_pair)
                            self.process(event.src_path, module_instance)
                    # NEED A REVIEW OF THIS ADD !!!!!!!!
                    elif path_pattern_suffix and '/*' in path_pattern_suffix and path_pattern_suffix.replace('/*', '') in event.src_path.lower() and re.search(file_regex, os.path.basename(event.src_path)):
                        self.last_processed.add(file_module_pair)
                        self.process(event.src_path, module_instance)

                    elif path_pattern_suffix and file_regex.pattern:  # If path/file name both specified, the directory of the event file must end with the path in config
                        if os.path.dirname(event.src_path).lower().endswith(path_pattern_suffix.lower()) and re.search(file_regex, os.path.basename(event.src_path)):
                            self.last_processed.add(file_module_pair)
                            self.process(event.src_path, module_instance)
                    elif not path_pattern_suffix and file_regex.pattern:  # If on_close triggered, the filename regex already matched
                        if re.search(file_regex, os.path.basename(event.src_path)):
                            self.last_processed.add(file_module_pair)
                            self.process(event.src_path, module_instance)

    def handle_directory_event(self, event, module_instance: OsirModuleModel):
        """
        Processes directory events that match configured patterns and sets up checks for idleness.

        Args:
            event: The event object representing the directory event.
            module_info (dict): Dictionary containing module information.
        """
        current_time = time.time()
        self.last_modified_times[event.src_path] = current_time

        # Check directory size immediately and store it
        current_size = self._get_directory_size(event.src_path)
        self.last_size[event.src_path] = current_size

        # Start a new timer to check for idleness
        timer = Timer(self.cooldown, self._check_for_idle, [event.src_path, module_instance])
        try:
            logger.debug(f"{module_instance.module_name} Starting timer for IDLE check of '{event.src_path}'")
            with self.timers_lock:
                self.active_timers.add(event.src_path)
            timer.start()
            logger.debug(f"{module_instance.module_name} Timer started for IDLE check of '{event.src_path}'")
        except Exception as e:
            logger.debug(f"{module_instance.module_name} Timer error for {event.src_path}. {str(e)}")
        logger.debug(f"{module_instance.module_name} Directory '{event.src_path}' is busy")

    def _get_directory_size(self, path: str) -> int:
        root = Path(path)
        total = 0

        for f in root.rglob('*'):
            try:
                if f.is_file():
                    total += f.stat().st_size
            except OSError:
                # Just skip unreadable entries
                continue

        return total

    def _check_parent(self, path, module_instance: OsirModuleModel):
        logger.debug(f"Checking if {module_instance.module_name} idle is not parent of another idle")
        # Convert path to a Path object
        path = Path(path).resolve()
        for current_idle_path in list(self.active_timers):
            current_idle_path_resolved = Path(current_idle_path).resolve()
            # Check if the current path is a parent of the active timer path
            if current_idle_path_resolved.is_relative_to(path) and path != current_idle_path_resolved:
                logger.debug(f"{module_instance.module_name} is parent of {current_idle_path}, the module can't be executed")
                return False
        return True

    def _check_for_idle(self, path, module_instance: OsirModuleModel):
        """
        Checks if the directory has been idle based on size changes and triggers further processing if idle.

        Args:
            path (str): Path to the directory being monitored.
            module_info (dict): Dictionary containing module information.
        """
        logger.debug(f"Starting _check_for_idle for {path} - {module_instance.module_name}")
        current_size = self._get_directory_size(path)
        previous_size = self.last_size.get(path, 0)

        if current_size == previous_size and self._check_parent(path, module_instance):
            logger.debug(f"{module_instance.module_name} Directory '{path}' is now idle")
            self.process(path, module_instance)
            with self.timers_lock:
                if path in self.active_timers:
                    self.active_timers.remove(path)
        else:
            logger.debug(f"{module_instance.module_name} Directory '{path}' is still busy, rescheduling check")
            # Reschedule the check if the directory size has changed
            self.last_size[path] = current_size
            timer = Timer(self.cooldown, self._check_for_idle, [path, module_instance])
            timer.start()

    def process(self, file_math: Path, module_instance: OsirModuleModel):
        """
            Initiates processing of a directory based on the module configuration.

            Args:
                directory_path (str): Path to the directory to be processed.
                module_info (dict): Dictionary containing module information.
        """

        logger.debug(f"""{module_instance.module_name}.yaml - Processing : \n
                    Case Path : {self.case_path} \n
                    File Math : {Path(file_math).relative_to(self.case_path)} \n""")

        module_instance = copy.deepcopy(module_instance)

        module_instance.input.match = file_math

        self._push_task(module_instance)

    def _push_task(self, module_instance: OsirModuleModel):
        """
            Pushes a task to the task queue for processing based on the current module configuration.

            Args:
                module_instance: The module instance to be processed.
        """
        task_params = (normalize_osir_path(self.case_path), module_instance, self.case_uuid, self.handler_uuid)
        TaskService.push_task(*task_params)

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

from collections import defaultdict

logger = AppLogger(__name__).get_logger()


class _CompiledRule:
    """Pre-compiled module rule for O(1) hot-path dispatch."""
    __slots__ = (
        'module', 'module_name', 'input_type',
        'output_dir', 'alt_output_dir',
        'output_dir_str', 'alt_output_dir_str',
        'patterns',
        'ext_anchors', 'basename_anchors',
    )

    def __init__(
        self,
        module,
        module_name,
        input_type,
        output_dir,
        alt_output_dir,
        output_dir_str,
        alt_output_dir_str,
        patterns,
        ext_anchors,
        basename_anchors,
    ):
        self.module = module
        self.module_name = module_name
        self.input_type = input_type

        self.output_dir = output_dir
        self.alt_output_dir = alt_output_dir

        self.output_dir_str = output_dir_str
        self.alt_output_dir_str = alt_output_dir_str

        self.patterns = patterns
        self.ext_anchors = ext_anchors
        self.basename_anchors = basename_anchors


class _LegacyRule:
    """Pre-compiled legacy module rule."""
    __slots__ = (
        'module_instance', 'module_name', 'input_type', 'module_path',
        'file_regex', 'path_pattern_suffix', 'wildcard_pattern',
        'is_path_regex', 'path_regex',
    )

    def __init__(
        self,
        module_instance,
        module_name,
        input_type,
        module_path,
        file_regex,
        path_pattern_suffix,
        wildcard_pattern,
        is_path_regex,
        path_regex,
    ):
        self.module_instance = module_instance
        self.module_name = module_name
        self.input_type = input_type
        self.module_path = module_path
        self.file_regex = file_regex
        self.path_pattern_suffix = path_pattern_suffix
        self.wildcard_pattern = wildcard_pattern
        self.is_path_regex = is_path_regex
        self.path_regex = path_regex


class CaseSnapshot:
    """Iterative directory snapshot used for change detection between scan cycles."""

    def __init__(self, case_path):
        self.case_path = case_path
        self.entries: set = set()

    def scan_directory(self):
        """Scan the full directory tree iteratively and store as a set."""
        entries: set = set()
        entries.add((self.case_path, 'directory'))
        stack = [self.case_path]

        while stack:
            current = stack.pop()
            try:
                with os.scandir(current) as it:
                    for entry in it:
                        try:
                            if entry.is_dir():
                                entries.add((entry.path, 'directory'))
                                stack.append(entry.path)
                            elif entry.is_file():
                                entries.add((entry.path, 'file'))
                        except OSError as e:
                            logger.warning(f"Unreadable entry: {entry}. Error: {e}")
            except OSError as e:
                logger.warning(f"Cannot scan directory: {current}. Error: {e}")

        self.entries = entries

    def get_entries_set(self) -> set:
        return self.entries


class ModuleHandler(FileSystemEventHandler):
    """
    Handles file system events to trigger processing modules based on file or directory changes.
    """

    def __init__(
        self,
        case_path: Path,
        cooldown_period: int,
        module_instances: list[OsirModuleModel],
        case_uuid,
        handler_uuid=None,
    ):
        self.handler_uuid = handler_uuid if handler_uuid else uuid.uuid4()
        self.cooldown = cooldown_period
        self.watch_directory = case_path
        self.case_path = case_path
        self._case_path_str = os.path.abspath(str(case_path))

        self.last_modified_times = {}
        self.module_instances: list[OsirModuleModel] = module_instances
        self.case_uuid = case_uuid

        self.last_mtime: dict[str, float] = {}
        self.last_processed: set = set()

        self.agent_config = OsirAgentConfig()

        self._task_counter_lock = threading.Lock()
        self._tasks_pushed_by_module = defaultdict(int)

        self._seen_prefix_lock = threading.Lock()

        # Dedup cache:
        # key:
        #   (module_name, file_size, hash_mode, file_hash)
        # value:
        #   first file path seen with this same key
        self._seen_prefix: dict[tuple, str] = {}

        self.active_timers: set = set()
        self.timers_lock = threading.Lock()

        self._virtual_dir = (Path(case_path) / 'virtual').resolve()
        self._virtual_dir_str = os.path.abspath(str(Path(case_path) / 'virtual'))

        self._dir_rules: list[_CompiledRule] = []
        self._file_rules_by_ext: dict[str, list[_CompiledRule]] = {}
        self._file_rules_by_basename: dict[str, list[_CompiledRule]] = {}
        self._file_rules_unindexed: list[_CompiledRule] = []
        self._legacy_file_rules: list[_LegacyRule] = []
        self._legacy_dir_rules: list[_LegacyRule] = []

        self._compile_rules(case_path, module_instances)

        # For some modules, duplicate detection requires full-file hash.
        self._full_hash_dedup_modules = {
            "evtx",
        }

        with OsirDb() as db:
            db.handler.create(
                handler_id=self.handler_uuid,
                case_uuid=self.case_uuid,
                modules=[module.module_name for module in module_instances],
                task_ids=[],
            )

    # ------------------------------------------------------------------
    # Rule compilation
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_glob_anchors(pattern: str) -> set[str]:
        """Extract a literal extension or basename anchor from a glob pattern."""
        last_seg = pattern.rstrip('/').split('/')[-1].lower()

        if not last_seg:
            return set()

        if not any(c in last_seg for c in ['*', '?', '[']):
            _, ext = os.path.splitext(last_seg)
            return {ext} if ext else {last_seg}

        if last_seg.startswith('*.') and last_seg.count('*') == 1 and '?' not in last_seg:
            return {last_seg[1:]}

        return set()

    @staticmethod
    def _glob_to_compiled_re(pattern: str) -> re.Pattern:
        """Convert a glob pattern (Path.match semantics) to a compiled regex.

        Relative patterns match from the right; absolute patterns match from the left.
        '*' matches any characters except '/'; '**' matches zero or more path components.
        """
        pat = pattern.replace('\\', '/')
        is_absolute = pat.startswith('/')
        parts = pat.lstrip('/').split('/')

        seg_regexes = []
        for part in parts:
            if part == '**':
                seg_regexes.append('**')
            else:
                seg = re.escape(part).replace(r'\*', '[^/]*').replace(r'\?', '[^/]')
                seg_regexes.append(seg)

        pieces = []
        for i, seg in enumerate(seg_regexes):
            if i == 0:
                pieces.append('(?:[^/]+/)*' if seg == '**' else seg)
            else:
                prev = seg_regexes[i - 1]
                if seg == '**':
                    pieces.append('/(?:[^/]+/)*')
                elif prev == '**':
                    pieces.append(seg)
                else:
                    pieces.append('/' + seg)

        body = ''.join(pieces)
        if is_absolute:
            return re.compile('^/' + body + '$')
        return re.compile('(?:^|/)' + body + '$')

    @staticmethod
    def _extract_regex_anchors(pattern: str) -> set[str]:
        """Extract literal extension anchors from a regex pattern."""
        m = re.search(r'\\\.([a-zA-Z0-9]+)\b', pattern)
        if m:
            return {'.' + m.group(1).lower()}

        m = re.search(r'\\\.\(([a-zA-Z0-9|]+)\)', pattern)
        if m:
            return {'.' + ext.lower() for ext in m.group(1).split('|')}

        return set()

    @staticmethod
    def _is_under_or_equal(path: str, root: str | None) -> bool:
        """
        Fast path containment check.

        Returns True when `path` is equal to `root` or located under `root`.
        """
        if not root:
            return False

        try:
            return os.path.commonpath([path, root]) == root
        except ValueError:
            return False

    def _consume_tasks_pushed_by_module(self) -> dict[str, int]:
        """
        Return task counters since the previous scan iteration, then reset them.
        """
        with self._task_counter_lock:
            counters = dict(self._tasks_pushed_by_module)
            self._tasks_pushed_by_module.clear()
            return counters

    def _compile_rules(self, case_path: Path, module_instances: list[OsirModuleModel]):
        """
        Pre-compile all module rules once at startup.
        """
        case_path_str = str(case_path)

        for module in module_instances:
            if not (hasattr(module.input, 'paths') and module.input.paths):
                path_pattern = module.input.path.rstrip('/') if module.input.path else None
                is_path_regex = (
                    path_pattern.startswith('r"') and path_pattern.endswith('"')
                    if path_pattern else False
                )

                legacy = _LegacyRule(
                    module_instance=module,
                    module_name=module.module_name,
                    input_type=module.input.type,
                    module_path=os.path.join(case_path_str, module.module_name),
                    file_regex=re.compile(module.input.name) if module.input.name else None,
                    path_pattern_suffix=path_pattern,
                    wildcard_pattern=path_pattern.rstrip('/*') if path_pattern else None,
                    is_path_regex=is_path_regex,
                    path_regex=re.compile(path_pattern[2:-1]) if is_path_regex else None,
                )

                if module.input.type == "dir":
                    self._legacy_dir_rules.append(legacy)
                else:
                    self._legacy_file_rules.append(legacy)

                continue

            output_dir = (Path(case_path) / module.module_name).resolve()
            output_dir_str = os.path.abspath(str(output_dir))

            alt_output_dir = None
            alt_output_dir_str = None

            if module.output.output_dir and '{case_path}' in module.output.output_dir:
                try:
                    alt_output_dir = Path(
                        remove_placeholders(
                            module.output.output_dir.replace('{case_path}', case_path_str)
                        )
                    ).resolve()
                    alt_output_dir_str = os.path.abspath(str(alt_output_dir))
                except Exception:
                    pass

            patterns: list[re.Pattern] = []
            ext_anchors: set[str] = set()
            basename_anchors: set[str] = set()
            all_anchored = True

            for pat in module.input.paths:
                pat = pat.replace("{case_path}", case_path_str)

                if pat.startswith(('r"', "r'")):
                    raw = pat[2:-1]
                    anchors = self._extract_regex_anchors(raw)
                    compiled = re.compile(raw)
                elif any(c in pat for c in ['^', '$', '(', '|']):
                    anchors = self._extract_regex_anchors(pat)
                    compiled = re.compile(pat)
                else:
                    anchors = self._extract_glob_anchors(pat)
                    compiled = self._glob_to_compiled_re(pat)

                patterns.append(compiled)

                if all_anchored:
                    if not anchors:
                        all_anchored = False
                    else:
                        for anchor in anchors:
                            if anchor.startswith('.'):
                                ext_anchors.add(anchor)
                            else:
                                basename_anchors.add(anchor)

            rule = _CompiledRule(
                module=module,
                module_name=module.module_name,
                input_type=module.input.type,
                output_dir=output_dir,
                alt_output_dir=alt_output_dir,
                output_dir_str=output_dir_str,
                alt_output_dir_str=alt_output_dir_str,
                patterns=patterns,
                ext_anchors=frozenset(ext_anchors),
                basename_anchors=frozenset(basename_anchors),
            )

            if module.input.type == "dir":
                self._dir_rules.append(rule)
            else:
                if all_anchored and (ext_anchors or basename_anchors):
                    for ext in ext_anchors:
                        self._file_rules_by_ext.setdefault(ext, []).append(rule)

                    for basename in basename_anchors:
                        self._file_rules_by_basename.setdefault(basename, []).append(rule)
                else:
                    self._file_rules_unindexed.append(rule)

        indexed = (
            sum(len(v) for v in self._file_rules_by_ext.values()) +
            sum(len(v) for v in self._file_rules_by_basename.values())
        )

        logger.debug(
            f"Rules compiled: {len(self._dir_rules)} dir | "
            f"{indexed} indexed file | "
            f"{len(self._file_rules_unindexed)} unindexed file | "
            f"{len(self._legacy_dir_rules) + len(self._legacy_file_rules)} legacy"
        )

    # ------------------------------------------------------------------
    # Directory monitoring loop
    # ------------------------------------------------------------------

    def monitor_directory(self, case_path, interval=5, reprocess=False):
        """
        Monitors the directory for changes at specified intervals.
        """
        casesnapshot = CaseSnapshot(case_path)

        if not reprocess:
            logger.debug(f"Fetching previously stored entries for case_uuid={self.case_uuid}")
            with OsirDb() as db:
                previous_entries = set(db.snapshot.get_stored_case_snapshot(case_path))

            if not previous_entries:
                logger.debug("No previous entries found, starting with an empty set.")
        else:
            previous_entries = set()

        scan_iterations = 0

        while True:
            scan_iterations += 1
            iteration_start_time = time.time()
            logger.debug("Scanning for new files/folders")

            scan_case_start_time = time.time()
            casesnapshot.scan_directory()
            current_entries = casesnapshot.get_entries_set()
            scan_case_duration = time.time() - scan_case_start_time

            logger.debug(f"Time taken to scan case: {scan_case_duration:.4} seconds.")

            new_entries = current_entries - previous_entries
            n_new_entries = len(new_entries)
            new_entries_duration = 0.0

            if new_entries:
                new_entries_start_time = time.time()
                logger.debug(f"New files/folders detected : {n_new_entries} new items")

                for entry in new_entries:
                    item_path, entry_type = entry

                    if entry_type == 'file':
                        self.on_created(FileCreatedEvent(item_path))
                    elif entry_type == 'directory':
                        self.on_created(DirCreatedEvent(item_path))

                new_entries_duration = time.time() - new_entries_start_time
                logger.debug(f"Time taken to process new items: {new_entries_duration:.4} seconds")
            else:
                logger.debug("No new item detected. Checking if a task is still ongoing before exiting...")

                with OsirDb() as db:
                    if not db.handler.is_processing_active(self.handler_uuid):
                        with self.timers_lock:
                            if not self.active_timers:
                                logger.debug("Case snapshot is being saved before exiting...")
                                db.snapshot.store_case_snapshot(
                                    self.case_uuid,
                                    case_path,
                                    list(current_entries),
                                )

                                if db.handler.check_handler_failure(self.handler_uuid):
                                    db.handler.update(self.handler_uuid, "processing_failed")
                                else:
                                    db.handler.update(self.handler_uuid, "processing_done")

                                exit()

            iteration_duration = time.time() - iteration_start_time

            tasks_pushed_by_module = self._consume_tasks_pushed_by_module()

            if tasks_pushed_by_module:
                tasks_summary = ", ".join(
                    f"{module_name}={count}"
                    for module_name, count in sorted(tasks_pushed_by_module.items())
                )
            else:
                tasks_summary = "none"

            logger.info(
                f"Scan iteration {scan_iterations}: {iteration_duration:.2f}s total "
                f"(dir scan: {scan_case_duration:.2f}s, entry processing: {new_entries_duration:.2f}s, "
                f"{n_new_entries} new entries, tasks pushed: {tasks_summary})"
            )

            previous_entries = current_entries

            time.sleep(interval)

    # ------------------------------------------------------------------
    # Event dispatch
    # ------------------------------------------------------------------

    def _dispatch_rule(self, event, src_abs: str, rule: _CompiledRule):
        """Match one pre-compiled rule against an event and trigger processing if it matches."""

        if self._is_under_or_equal(src_abs, rule.output_dir_str):
            return

        if self._is_under_or_equal(src_abs, rule.alt_output_dir_str):
            return

        if self._is_under_or_equal(src_abs, self._virtual_dir_str) and f"{os.sep}fs{os.sep}" not in src_abs:
            return

        file_module_pair = (event.src_path, rule.module_name)

        if file_module_pair in self.last_processed:
            return

        for pat in rule.patterns:
            if not pat.search(src_abs):
                continue

            logger.info(
                f"MATCH: {src_abs} avec {pat.pattern} (Module: {rule.module_name})"
            )

            self.last_processed.add(file_module_pair)

            if rule.input_type == "dir":
                self.handle_directory_event(event, rule.module)
            else:
                try:
                    (
                        is_duplicate,
                        duplicate_of,
                        hash_mode,
                        file_hash,
                        file_size,
                    ) = self._check_duplicate_by_hash(
                        module_name=rule.module_name,
                        file_path=event.src_path,
                        prefix_size=81920,
                    )

                    if is_duplicate:
                        logger.info(
                            f"{rule.module_name} - Skipping duplicate file: "
                            f"skipped_file='{event.src_path}' | "
                            f"same_hash_as='{duplicate_of}' | "
                            f"hash_mode='{hash_mode}' | "
                            f"size={file_size} | "
                            f"xxh3_128='{file_hash}'"
                        )
                        return

                except Exception as e:
                    logger.warning(
                        f"{rule.module_name} - Hash dedup failed for {event.src_path}: {e}"
                    )

                self.process(event.src_path, rule.module)

            break

    def on_created(self, event):
        """Dispatch a file/directory creation event to all matching module rules."""
        if not hasattr(event, 'src_path'):
            logger.warning("Event without path, ignored.")
            return

        src_abs = os.path.abspath(event.src_path)

        if event.is_directory:
            for rule in self._dir_rules:
                self._dispatch_rule(event, src_abs, rule)

            for rule in self._legacy_dir_rules:
                self._on_created_legacy(event, rule)

        else:
            src_lower = event.src_path.lower()
            ext = os.path.splitext(src_lower)[1]
            basename = os.path.basename(src_lower)

            seen: set[int] = set()

            for rule in self._file_rules_by_ext.get(ext, ()):
                seen.add(id(rule))
                self._dispatch_rule(event, src_abs, rule)

            for rule in self._file_rules_by_basename.get(basename, ()):
                if id(rule) not in seen:
                    seen.add(id(rule))
                    self._dispatch_rule(event, src_abs, rule)

            for rule in self._file_rules_unindexed:
                self._dispatch_rule(event, src_abs, rule)

            for rule in self._legacy_file_rules:
                self._on_created_legacy(event, rule)

    def _on_created_legacy(self, event, rule: _LegacyRule):
        """Legacy dispatch path for modules using input.path/input.name."""
        file_module_pair = (event.src_path, rule.module_name)
        module_path = rule.module_path
        input_type = rule.input_type
        path_pattern_suffix = rule.path_pattern_suffix
        wildcard_pattern = rule.wildcard_pattern
        file_regex = rule.file_regex
        is_path_regex = rule.is_path_regex
        path_regex = rule.path_regex

        if (
            str(module_path) not in str(event.src_path)
            and input_type == "dir"
            and event.is_directory
        ):
            if is_path_regex and path_regex.search(str(event.src_path)):
                logger.debug(
                    f"{rule.module_name} Directory '{event.src_path}' will be processed "
                    f"(regex match)"
                )
                self.handle_directory_event(event, rule.module_instance)

            elif (
                path_pattern_suffix == "{case_path}"
                and str(event.src_path) == str(self.case_path)
            ):
                logger.debug(f"{rule.module_name} Directory '{event.src_path}' will be processed")
                self.handle_directory_event(event, rule.module_instance)

            elif (
                path_pattern_suffix
                and "{case_path}" in path_pattern_suffix
                and event.src_path == path_pattern_suffix.replace("{case_path}", str(self.case_path))
            ):
                logger.debug(f"{rule.module_name} Directory '{event.src_path}' will be processed")
                self.handle_directory_event(event, rule.module_instance)

            elif (
                path_pattern_suffix
                and path_pattern_suffix.endswith('/*')
                and os.path.dirname(event.src_path).lower().endswith(wildcard_pattern.lower())
            ):
                logger.debug(f"{rule.module_name} Directory '{event.src_path}' will be processed")
                self.handle_directory_event(event, rule.module_instance)

            elif path_pattern_suffix and str(event.src_path).lower().endswith(
                path_pattern_suffix.lower()
            ):
                logger.debug(f"{rule.module_name} Directory '{event.src_path}' will be processed")
                self.handle_directory_event(event, rule.module_instance)

        elif (
            str(module_path) not in str(os.path.dirname(event.src_path))
            and input_type == "file"
            and not event.is_directory
            and file_module_pair not in self.last_processed
        ):
            if is_path_regex and path_regex.search(event.src_path):
                if file_regex is not None and re.search(file_regex, os.path.basename(event.src_path)):
                    self.last_processed.add(file_module_pair)
                    self.process(event.src_path, rule.module_instance)

            elif path_pattern_suffix and file_regex is not None and not file_regex.pattern:
                if event.src_path.lower().endswith(path_pattern_suffix.lower()):
                    self.last_processed.add(file_module_pair)
                    self.process(event.src_path, rule.module_instance)

            elif (
                path_pattern_suffix
                and '/*' in path_pattern_suffix
                and path_pattern_suffix.replace('/*', '') in event.src_path.lower()
                and file_regex is not None
                and re.search(file_regex, os.path.basename(event.src_path))
            ):
                self.last_processed.add(file_module_pair)
                self.process(event.src_path, rule.module_instance)

            elif path_pattern_suffix and file_regex is not None and file_regex.pattern:
                if (
                    os.path.dirname(event.src_path).lower().endswith(path_pattern_suffix.lower())
                    and re.search(file_regex, os.path.basename(event.src_path))
                ):
                    self.last_processed.add(file_module_pair)
                    self.process(event.src_path, rule.module_instance)

            elif not path_pattern_suffix and file_regex is not None and file_regex.pattern:
                if re.search(file_regex, os.path.basename(event.src_path)):
                    self.last_processed.add(file_module_pair)
                    self.process(event.src_path, rule.module_instance)

    # ------------------------------------------------------------------
    # Directory idle detection
    # ------------------------------------------------------------------

    def handle_directory_event(self, event, module_instance: OsirModuleModel):
        """
        Processes directory events that match configured patterns and sets up checks for idleness.
        """
        self.last_modified_times[event.src_path] = time.time()
        self.last_mtime[event.src_path] = self._get_directory_mtime(event.src_path)

        timer = Timer(self.cooldown, self._check_for_idle, [event.src_path, module_instance])

        try:
            logger.debug(
                f"{module_instance.module_name} Starting timer for IDLE check of "
                f"'{event.src_path}'"
            )

            with self.timers_lock:
                self.active_timers.add(event.src_path)

            timer.start()

            logger.debug(
                f"{module_instance.module_name} Timer started for IDLE check of "
                f"'{event.src_path}'"
            )

        except Exception as e:
            logger.debug(f"{module_instance.module_name} Timer error for {event.src_path}. {str(e)}")

        logger.debug(f"{module_instance.module_name} Directory '{event.src_path}' is busy")

    def _get_directory_mtime(self, path: str) -> float:
        """Return directory mtime."""
        try:
            return os.stat(path).st_mtime
        except OSError:
            return 0.0

    def _check_parent(self, path, module_instance: OsirModuleModel):
        logger.debug(f"Checking if {module_instance.module_name} idle is not parent of another idle")

        path = Path(path).resolve()

        for current_idle_path in list(self.active_timers):
            current_idle_path_resolved = Path(current_idle_path).resolve()

            if current_idle_path_resolved.is_relative_to(path) and path != current_idle_path_resolved:
                logger.debug(
                    f"{module_instance.module_name} is parent of {current_idle_path}, "
                    f"the module can't be executed"
                )
                return False

        return True

    def _check_for_idle(self, path, module_instance: OsirModuleModel):
        """
        Checks if the directory has been idle and triggers processing if idle.
        """
        logger.debug(f"Starting _check_for_idle for {path} - {module_instance.module_name}")

        current_mtime = self._get_directory_mtime(path)
        previous_mtime = self.last_mtime.get(path, 0.0)

        if current_mtime == previous_mtime and self._check_parent(path, module_instance):
            logger.debug(f"{module_instance.module_name} Directory '{path}' is now idle")
            self.process(path, module_instance)

            with self.timers_lock:
                if path in self.active_timers:
                    self.active_timers.remove(path)

        else:
            logger.debug(
                f"{module_instance.module_name} Directory '{path}' is still busy, "
                f"rescheduling check"
            )
            self.last_mtime[path] = current_mtime

            timer = Timer(self.cooldown, self._check_for_idle, [path, module_instance])
            timer.start()

    # ------------------------------------------------------------------
    # Task dispatch
    # ------------------------------------------------------------------

    def process(self, file_match: Path, module_instance: OsirModuleModel):
        """
        Initiates processing of a file or directory based on the module configuration.
        """
        logger.debug(
            f"""{module_instance.module_name}.yaml - Processing : \n
                    Case Path : {self.case_path} \n
                    File Match : {Path(file_match).relative_to(self.case_path)} \n"""
        )

        module_instance = copy.deepcopy(module_instance)
        module_instance.input.match = str(file_match)

        self._push_task(module_instance)

    def _push_task(self, module_instance: OsirModuleModel):
        """
        Pushes a task to the task queue.
        """
        task_params = (
            normalize_osir_path(self.case_path),
            module_instance,
            self.case_uuid,
            self.handler_uuid,
        )

        TaskService.push_task(*task_params)

        with self._task_counter_lock:
            self._tasks_pushed_by_module[module_instance.module_name] += 1

    # ------------------------------------------------------------------
    # Dedup helpers
    # ------------------------------------------------------------------

    def _check_duplicate_by_hash(
        self,
        module_name: str,
        file_path: str,
        prefix_size: int = 8192,
    ) -> tuple[bool, str | None, str, str, int]:
        """
        Checks whether a file should be considered a duplicate.

        Default behavior:
            Uses xxh3_128 over the first `prefix_size` bytes.

        Exception behavior:
            For modules listed in self._full_hash_dedup_modules, hashes the whole file.

        Dedup scope:
            Per module, file size, hash mode, and hash value.

        Returns:
            (
                is_duplicate,
                duplicate_of,
                hash_mode,
                file_hash,
                file_size,
            )

        Example:
            If file B has the same dedup key as file A:

            (
                True,
                "/path/to/file_A.evtx",
                "full",
                "abc123...",
                123456
            )
        """
        from osir_lib.core.OsirUtils import (
            compute_file_xxh3_128_prefix,
            compute_file_xxh3_128_full,
        )

        try:
            file_size = os.path.getsize(file_path)
        except Exception:
            file_size = -1

        if module_name in self._full_hash_dedup_modules:
            hash_mode = "full"
            file_hash = compute_file_xxh3_128_full(file_path)
        else:
            hash_mode = f"prefix:{prefix_size}"
            file_hash = compute_file_xxh3_128_prefix(file_path, prefix_size=prefix_size)

        key = (module_name, file_size, hash_mode, file_hash)

        with self._seen_prefix_lock:
            duplicate_of = self._seen_prefix.get(key)

            if duplicate_of is not None:
                return True, duplicate_of, hash_mode, file_hash, file_size

            self._seen_prefix[key] = file_path
            return False, None, hash_mode, file_hash, file_size
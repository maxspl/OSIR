import re
import time
import os
import json
import threading
import copy

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Timer
import uuid

from osir_lib.core.OsirUtils import normalize_osir_path
from osir_lib.core.OsirUtils import (
    compute_file_xxh3_128_prefix,
    compute_file_xxh3_128_full,
)
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from watchdog.events import DirCreatedEvent, FileCreatedEvent
from watchdog.events import FileSystemEventHandler
from osir_lib.core.OsirUtils import remove_placeholders
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
        'output_dir_pref', 'alt_output_dir_pref',
        'task_name', 'queue', 'processor_os', 'base_dump',
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
        task_name=None,
        queue=None,
        processor_os=None,
        base_dump=None,
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

        # Precomputed "root + sep" prefixes: str.startswith is ~30x cheaper
        # than os.path.commonpath on the hot path.
        self.output_dir_pref = (output_dir_str + os.sep) if output_dir_str else None
        self.alt_output_dir_pref = (alt_output_dir_str + os.sep) if alt_output_dir_str else None

        # Precomputed once: avoids per-task deepcopy + pydantic
        # serialization on the push hot path.
        self.task_name = task_name
        self.queue = queue
        self.processor_os = processor_os
        self.base_dump = base_dump


class _LegacyRule:
    """Pre-compiled legacy module rule."""
    __slots__ = (
        'module_instance', 'module_name', 'input_type', 'module_path',
        'file_regex', 'path_pattern_suffix', 'wildcard_pattern',
        'is_path_regex', 'path_regex',
        'suffix_lower', 'wildcard_lower', 'wildcard_body_lower', 'has_wildcard',
        'regex_has_pattern',
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

        # Hot-path precomputations (these were recomputed per event before).
        self.suffix_lower = path_pattern_suffix.lower() if path_pattern_suffix else None
        self.wildcard_lower = wildcard_pattern.lower() if wildcard_pattern else None
        self.wildcard_body_lower = (
            path_pattern_suffix.replace('/*', '').lower() if path_pattern_suffix else None
        )
        self.has_wildcard = bool(path_pattern_suffix and '/*' in path_pattern_suffix)
        self.regex_has_pattern = bool(file_regex is not None and file_regex.pattern)


class CaseSnapshot:
    """Iterative directory snapshot used for change detection between scan cycles."""

    def __init__(self, case_path):
        # Normalize to str: os.scandir yields str paths, so the synthetic
        # root entry must be a str too. A PosixPath here leaks into
        # DirCreatedEvent.src_path and breaks substring matching in the
        # legacy dispatch ("'PosixPath' is not iterable"), and would also
        # mismatch entries persisted from previous runs.
        self.case_path = str(case_path)
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

        self._task_counter_lock = threading.Lock()
        self._tasks_pushed_by_module = defaultdict(int)

        self._seen_prefix_lock = threading.Lock()

        # Batched task creation:
        # file events matched by compiled rules are buffered here, then
        # hashed in parallel and pushed in bulk (one DB round trip + one
        # AMQP producer per batch) instead of one connection per task.
        # Batches are processed on a background executor so hashing/push
        # overlaps with directory scanning and rule dispatch.
        self._pending_lock = threading.Lock()
        self._pending_file_tasks: list[tuple[str, _CompiledRule]] = []
        self._push_batch_size = 10000
        self._hash_workers = min(16, (os.cpu_count() or 4) * 2)
        self._case_path_norm = normalize_osir_path(case_path)
        self._flush_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="osir-flush")
        self._flush_futures: list = []
        self._flush_futures_lock = threading.Lock()

        # Dedup cache:
        # key:
        #   (module_name, file_size, hash_mode, file_hash)
        # value:
        #   first file path seen with this same key
        self._seen_prefix: dict[tuple, str] = {}

        # File stability gate:
        # Do not push file tasks as soon as a path appears in the case tree.
        # A producer may still be copying, extracting or streaming the file.
        # The watchdog keeps unstable file matches here and releases them only
        # after size + mtime are stable for a short window. This replaces the
        # old per-task sleep in workers for the normal watchdog path.
        self._file_stability_window = float(os.getenv("OSIR_FILE_STABILITY_WINDOW", "1.0"))
        self._file_stability_state: dict[str, tuple[int, int, float]] = {}
        self._unstable_file_tasks: dict[tuple[str, str, str], tuple[str, object]] = {}
        self._unstable_lock = threading.Lock()

        self.active_timers: set = set()
        self.timers_lock = threading.Lock()

        # Directory events deferred behind a hold_consumers barrier.
        self._deferred: dict = {}

        self._virtual_dir = (Path(case_path) / 'virtual').resolve()
        self._virtual_dir_str = os.path.abspath(str(Path(case_path) / 'virtual'))
        self._virtual_dir_pref = self._virtual_dir_str + os.sep
        self._fs_seg = f"{os.sep}fs{os.sep}"

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
            # Indexer sur l'extension FINALE (semantique os.path.splitext).
            final_ext = '.' + last_seg[1:].rsplit('.', 1)[-1]
            return {final_ext} if len(final_ext) > 1 else set()

        # General wildcard segment with a literal final extension:
        # e.g. 'uac-*.tar.gz' -> '.gz', 'processeswmi*.csv' -> '.csv'.
        # The final extension is a correct superset anchor: every glob match
        # necessarily ends with it.
        if '.' in last_seg:
            tail = last_seg.rsplit('.', 1)[-1]
            if tail and not any(c in tail for c in ['*', '?', '[', ']']):
                return {'.' + tail}

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
    def _has_top_level_alternation(pattern: str) -> bool:
        """True if a '|' exists outside of any group (...) or character class [...]."""
        depth = 0
        in_class = False
        i = 0
        n = len(pattern)
        while i < n:
            c = pattern[i]
            if c == '\\':
                i += 2
                continue
            if in_class:
                if c == ']':
                    in_class = False
            elif c == '[':
                in_class = True
            elif c == '(':
                depth += 1
            elif c == ')':
                if depth > 0:
                    depth -= 1
            elif c == '|' and depth == 0:
                return True
            i += 1
        return False

    @staticmethod
    def _extract_regex_anchors(pattern: str) -> set[str]:
        """Extract literal extension anchors from a regex pattern.

        The file index is keyed on os.path.splitext()[1], so only the LAST
        extension (the one anchored at the end of the pattern) is usable.
        r"\\.7z\\.p7b$" must be anchored on '.p7b', never on '.7z'.

        Returns set() when the final extension cannot be determined with
        certainty: the rule then falls back to the unindexed list (correct).
        """
        # A top-level alternation means branches may have different suffixes
        # => cannot anchor safely.
        if ModuleHandler._has_top_level_alternation(pattern):
            return set()

        # Final literal extension: ...\.ext  (optionally followed by $)
        m = re.search(r'\\\.([a-zA-Z0-9]+)\$?$', pattern)
        if m:
            return {'.' + m.group(1).lower()}

        # Final alternation of extensions: ...\.(ext1|ext2)$ or ...\.(?:ext1|ext2)$
        m = re.search(r'\\\.\((?:\?:)?([a-zA-Z0-9|]+)\)\$?$', pattern)
        if m:
            return {'.' + e.lower() for e in m.group(1).split('|') if e}

        # Trailing literal basename: .../LITERAL$ (e.g. r".*/SOFTWARE$").
        # The '/' guarantees the basename of any match is exactly LITERAL,
        # making the basename index a correct superset filter.
        basename = ModuleHandler._literal_tail_basename(pattern)
        if basename:
            return {basename.lower()}

        return set()

    @staticmethod
    def _literal_tail_basename(pattern: str) -> str | None:
        """If the regex ends with '/<literal>$', return the unescaped literal.

        Returns None when the tail contains any active regex construct
        (the rule then stays unindexed, which is always correct).
        """
        if not pattern.endswith('$') or len(pattern) < 3:
            return None

        body = pattern[:-1]
        meta = set('.^$*+?{}[]()|')
        char_classes = set('dDwWsSbBAZ')

        tokens: list = []  # literal char, '/', or None (non-literal construct)
        i = 0
        n = len(body)
        while i < n:
            c = body[i]
            if c == '\\':
                if i + 1 >= n:
                    return None
                nxt = body[i + 1]
                tokens.append(None if nxt in char_classes else nxt)
                i += 2
            elif c == '/':
                tokens.append('/')
                i += 1
            elif c in meta:
                tokens.append(None)
                i += 1
            else:
                tokens.append(c)
                i += 1

        try:
            last_slash = len(tokens) - 1 - tokens[::-1].index('/')
        except ValueError:
            return None

        tail = tokens[last_slash + 1:]
        if not tail or any(t is None for t in tail):
            return None

        return ''.join(tail)

    @staticmethod
    def _combine_patterns(compiled_patterns) -> re.Pattern | None:
        """Merge several compiled patterns into one alternation usable as a
        cheap pre-filter (single C-level scan instead of N python-level
        searches). Returns None when merging would be unsafe (backrefs,
        named groups) or fails to compile -- callers must then fall back to
        per-rule matching.
        """
        parts = []
        for cp in compiled_patterns:
            pat = cp.pattern

            # Backreferences and named groups break inside a merged
            # alternation (group numbering becomes global).
            if re.search(r'\\[1-9]', pat) or '(?P<' in pat or '(?P=' in pat:
                return None

            # Inline global flags ('(?i)...') are only legal at the very
            # start of a pattern: rewrite to a scoped group '(?i:...)'.
            m = re.match(r'^\(\?([aiLmsux]+)\)', pat)
            if m:
                pat = f"(?{m.group(1)}:{pat[m.end():]})"

            parts.append(f"(?:{pat})")

        if not parts:
            return None

        try:
            return re.compile("|".join(parts))
        except re.error:
            return None
        
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

    def _is_barrier_consumer(self, src_abs: str, module_instance: OsirModuleModel) -> bool:
        """
        True when this is a directory-input module whose input directory lies
        under the output directory of a hold_consumers barrier producer.
        """
        if module_instance.input.type != "dir":
            return False
        if getattr(module_instance.configuration, 'hold_consumers', False):
            return False
        for barrier_dir in self._barrier_output_dirs:
            if self._is_under_or_equal(src_abs, barrier_dir):
                return True
        return False

    def _barriers_pending(self) -> bool:
        """
        True while at least one hold_consumers barrier producer still has a
        task in a non-terminal state for this case.
        """
        if not self._barrier_modules:
            return False

        with OsirDb() as db:
            row = db.execute_query(
                """
                SELECT COUNT(*) AS pending_count
                FROM osir_tasks t
                LEFT JOIN celery_taskmeta m ON m.task_id = t.task_id::text
                WHERE t.case_uuid = %s
                  AND t.module = ANY(%s)
                  AND COALESCE(m.status, 'PENDING') NOT IN ('SUCCESS', 'FAILURE', 'REVOKED')
                  AND NOT (
                      m.status IS NULL
                      AND t.processing_status IN ('processing_done', 'processing_failed')
                  )
                """,
                (str(self.case_uuid), self._barrier_modules),
                fetch="fetchone",
            )

        if not row:
            return False

        try:
            pending_count = int(row.get("pending_count", 0)) if isinstance(row, dict) else int(row[0] or 0)

            logger.debug(
                f"hold_consumers barrier status: "
                f"{pending_count} pending producer task(s) "
                f"for modules={self._barrier_modules}"
            )

            return pending_count > 0

        except Exception as e:
            logger.warning(f"Unable to parse hold_consumers barrier status: row={row!r}, error={e}")
            return False

    def _compile_rules(self, case_path: Path, module_instances: list[OsirModuleModel]):
        """
        Pre-compile all module rules once at startup.
        """
        case_path_str = str(case_path)

        # hold_consumers barriers: their output dir + module name.
        self._barrier_modules: list[str] = []
        self._barrier_output_dirs: list[str] = []
        for module in module_instances:
            if getattr(module.configuration, 'hold_consumers', False):
                self._barrier_modules.append(module.module_name)
                self._barrier_output_dirs.append(
                    os.path.abspath(os.path.join(case_path_str, module.module_name))
                )

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
                task_name=TaskService.get_task_name(module),
                queue=TaskService.get_queue_name(module),
                processor_os=module.configuration.processor_os,
                base_dump=module.model_dump(mode="json"),
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

        # Combined pre-filters: one C-level regex scan rejects the vast
        # majority of entries before any per-rule python loop runs.
        self._unindexed_prefilter = self._combine_patterns(
            [p for r in self._file_rules_unindexed for p in r.patterns]
        ) if self._file_rules_unindexed else None

        self._dir_prefilter = self._combine_patterns(
            [p for r in self._dir_rules for p in r.patterns]
        ) if self._dir_rules else None

        # Legacy pre-filters: one union search replaces N per-rule searches.
        # A miss on the union strictly implies a miss on every member, so
        # gating the individual searches behind these hints is semantically
        # exact (and _combine_patterns returns None -> hints stay True when
        # merging would be unsafe).
        self._legacy_path_prefilter = self._combine_patterns(
            [r.path_regex for r in self._legacy_file_rules if r.is_path_regex]
        ) if any(r.is_path_regex for r in self._legacy_file_rules) else None

        self._legacy_name_prefilter = self._combine_patterns(
            [
                r.file_regex for r in self._legacy_file_rules
                if not r.path_pattern_suffix and r.regex_has_pattern
            ]
        ) if any(
            not r.path_pattern_suffix and r.regex_has_pattern
            for r in self._legacy_file_rules
        ) else None

        logger.debug(
            f"Rules compiled: {len(self._dir_rules)} dir | "
            f"{indexed} indexed file | "
            f"{len(self._file_rules_unindexed)} unindexed file | "
            f"{len(self._legacy_dir_rules) + len(self._legacy_file_rules)} legacy | "
            f"prefilters: unindexed={'on' if self._unindexed_prefilter else 'off'}, "
            f"dir={'on' if self._dir_prefilter else 'off'}"
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

            released_stable_files = self._release_stable_file_tasks()

            if new_entries or released_stable_files:
                new_entries_start_time = time.time()
                if new_entries:
                    logger.debug(f"New files/folders detected : {n_new_entries} new items")
                if released_stable_files:
                    logger.debug(f"Released {released_stable_files} stable delayed file task(s)")

                for entry in new_entries:
                    item_path, entry_type = entry

                    if entry_type == 'file':
                        self.on_created(FileCreatedEvent(item_path))
                    elif entry_type == 'directory':
                        self.on_created(DirCreatedEvent(item_path))

                    # Stream batches to workers while the scan is still
                    # running; hashing/push happens on the background
                    # executor, overlapping with this dispatch loop.
                    if len(self._pending_file_tasks) >= self._push_batch_size:
                        self._flush_pending_file_tasks()

                self._flush_pending_file_tasks(wait=True)

                new_entries_duration = time.time() - new_entries_start_time
                logger.debug(f"Time taken to process new items: {new_entries_duration:.4} seconds")
            else:
                logger.debug("No new item detected. Checking if a task is still ongoing before exiting...")

                # Defensive: never exit with buffered, delayed or in-flight tasks.
                self._flush_pending_file_tasks(wait=True)

                if self._has_unstable_file_tasks():
                    logger.debug(
                        f"{self._unstable_file_task_count()} unstable file task(s) still waiting"
                    )
                else:
                    with OsirDb() as db:
                        if not db.handler.is_processing_active(self.handler_uuid):
                            with self.timers_lock:
                                if not self._deferred and not self.active_timers:
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

                                    # Monitor runs in a non-main thread: exit()
                                    # only kills this thread, so release the
                                    # executor's worker threads explicitly.
                                    self._flush_executor.shutdown(wait=True)

                                    exit()

            # Release directory events deferred behind a hold_consumers
            # barrier, once every barrier producer task has finished.
            if self._deferred and not self._barriers_pending():
                for key, (d_event, d_module) in list(self._deferred.items()):
                    del self._deferred[key]
                    logger.debug(
                        f"{d_module.module_name} hold_consumers barrier cleared, "
                        f"releasing deferred directory '{d_event.src_path}'"
                    )
                    self.handle_directory_event(d_event, d_module)

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
    # File stability gate
    # ------------------------------------------------------------------

    def _is_file_stable(self, path: str) -> bool:
        """Return True when a file is safe to process without blocking.

        Stable means either:
          - the file mtime is already older than OSIR_FILE_STABILITY_WINDOW; or
          - size + mtime have not changed for OSIR_FILE_STABILITY_WINDOW.

        This detects files still being copied, decompressed or streamed without
        adding a fixed sleep to every worker task.
        """
        try:
            st = os.stat(path)
        except OSError as e:
            logger.debug(f"File stability check skipped for unreadable file '{path}': {e}")
            return False

        now = time.monotonic()
        wall_now = time.time()
        size = int(st.st_size)
        mtime_ns = int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1_000_000_000)))

        # Fast path: most files discovered during a full scan are already old
        # enough. No sleep, no second stat.
        if wall_now - st.st_mtime >= self._file_stability_window:
            self._file_stability_state.pop(path, None)
            return True

        previous = self._file_stability_state.get(path)
        if previous is not None:
            previous_size, previous_mtime_ns, stable_since = previous
            if previous_size == size and previous_mtime_ns == mtime_ns:
                if now - stable_since >= self._file_stability_window:
                    self._file_stability_state.pop(path, None)
                    return True
            else:
                stable_since = now
        else:
            stable_since = now

        self._file_stability_state[path] = (size, mtime_ns, stable_since)
        return False

    def _queue_compiled_file_task_when_stable(self, path: str, rule: _CompiledRule) -> bool:
        """Queue a compiled-rule file task only when its input is stable."""
        if self._is_file_stable(path):
            with self._pending_lock:
                self._pending_file_tasks.append((path, rule))
            return True

        key = (path, rule.module_name, "compiled")
        with self._unstable_lock:
            self._unstable_file_tasks[key] = (path, rule)

        logger.debug(
            f"{rule.module_name} - file '{path}' is not stable yet; delaying task push"
        )
        return False

    def _queue_legacy_file_task_when_stable(self, path: str, module_instance: OsirModuleModel) -> bool:
        """Run a legacy file task only when its input is stable."""
        if self._is_file_stable(path):
            self.process(path, module_instance)
            return True

        key = (path, module_instance.module_name, "legacy")
        with self._unstable_lock:
            self._unstable_file_tasks[key] = (path, module_instance)

        logger.debug(
            f"{module_instance.module_name} - file '{path}' is not stable yet; delaying task push"
        )
        return False

    def _release_stable_file_tasks(self) -> int:
        """Release delayed file tasks whose input became stable."""
        with self._unstable_lock:
            delayed = list(self._unstable_file_tasks.items())

        released = 0
        for key, (path, target) in delayed:
            if not os.path.exists(path):
                with self._unstable_lock:
                    self._unstable_file_tasks.pop(key, None)
                self._file_stability_state.pop(path, None)
                _path, module_name, kind = key
                self.last_processed.discard((path, module_name))
                logger.debug(
                    f"Dropping delayed {kind} file task for missing file '{path}'"
                )
                continue

            if not self._is_file_stable(path):
                continue

            with self._unstable_lock:
                # Another thread may already have removed/replaced it.
                if self._unstable_file_tasks.pop(key, None) is None:
                    continue

            _path, _module_name, kind = key
            if kind == "compiled":
                with self._pending_lock:
                    self._pending_file_tasks.append((path, target))
            else:
                self.process(path, target)

            released += 1
            logger.debug(f"Released stable file task for '{path}'")

        return released

    def _has_unstable_file_tasks(self) -> bool:
        with self._unstable_lock:
            return bool(self._unstable_file_tasks)

    def _unstable_file_task_count(self) -> int:
        with self._unstable_lock:
            return len(self._unstable_file_tasks)

    # ------------------------------------------------------------------
    # Event dispatch
    # ------------------------------------------------------------------

    def _dispatch_rule(self, event, src_abs: str, rule: _CompiledRule):
        """Match one pre-compiled rule against an event and trigger processing if it matches.

        Hot-path ordering: the (C-level) regex search runs FIRST as a cheap
        rejector — for the vast majority of (entry, rule) pairs nothing else
        is evaluated. Containment/dedup checks only run on an actual match.
        """
        matched = None
        for pat in rule.patterns:
            if pat.search(src_abs):
                matched = pat
                break

        if matched is None:
            return

        # Exclusions (only evaluated on pattern match).
        if src_abs == rule.output_dir_str or (
            rule.output_dir_pref and src_abs.startswith(rule.output_dir_pref)
        ):
            return

        if rule.alt_output_dir_str and (
            src_abs == rule.alt_output_dir_str
            or src_abs.startswith(rule.alt_output_dir_pref)
        ):
            return

        file_module_pair = (event.src_path, rule.module_name)

        if file_module_pair in self.last_processed:
            return

        logger.debug(
            f"MATCH: {src_abs} avec {matched.pattern} (Module: {rule.module_name})"
        )

        self.last_processed.add(file_module_pair)

        if rule.input_type == "dir":
            self.handle_directory_event(event, rule.module)
        else:
            # Buffered after stability: hashing (dedup) and task push happen in
            # _process_pending_batch(), in parallel and in bulk. Unstable files
            # stay in _unstable_file_tasks and are retried by the scan loop.
            self._queue_compiled_file_task_when_stable(event.src_path, rule)

    def on_created(self, event):
        """Dispatch a file/directory creation event to all matching module rules."""
        if not hasattr(event, 'src_path'):
            logger.warning("Event without path, ignored.")
            return

        src_abs = os.path.abspath(event.src_path)

        # Virtual-dir exclusion is event-level (identical for every compiled
        # rule), so it is checked once here instead of once per rule.
        virtual_excluded = (
            (src_abs == self._virtual_dir_str or src_abs.startswith(self._virtual_dir_pref))
            and self._fs_seg not in src_abs
        )

        if event.is_directory:
            if not virtual_excluded and self._dir_rules:
                if self._dir_prefilter is None or self._dir_prefilter.search(src_abs):
                    for rule in self._dir_rules:
                        self._dispatch_rule(event, src_abs, rule)

            for rule in self._legacy_dir_rules:
                self._on_created_legacy(event, rule)

        else:
            if not virtual_excluded:
                src_lower = event.src_path.lower()
                ext = os.path.splitext(src_lower)[1]
                basename_lower = os.path.basename(src_lower)

                seen: set[int] = set()

                for rule in self._file_rules_by_ext.get(ext, ()):
                    seen.add(id(rule))
                    self._dispatch_rule(event, src_abs, rule)

                for rule in self._file_rules_by_basename.get(basename_lower, ()):
                    if id(rule) not in seen:
                        seen.add(id(rule))
                        self._dispatch_rule(event, src_abs, rule)

                if self._file_rules_unindexed:
                    if self._unindexed_prefilter is None or self._unindexed_prefilter.search(src_abs):
                        for rule in self._file_rules_unindexed:
                            self._dispatch_rule(event, src_abs, rule)

            if self._legacy_file_rules:
                dirname = os.path.dirname(event.src_path)
                basename = os.path.basename(event.src_path)
                src_lower_full = event.src_path.lower()
                dirname_lower = dirname.lower()

                path_hint = (
                    self._legacy_path_prefilter is None
                    or self._legacy_path_prefilter.search(event.src_path) is not None
                )
                name_hint = (
                    self._legacy_name_prefilter is None
                    or self._legacy_name_prefilter.search(basename) is not None
                )

                for rule in self._legacy_file_rules:
                    self._on_created_legacy(
                        event, rule,
                        dirname=dirname,
                        basename=basename,
                        src_lower=src_lower_full,
                        dirname_lower=dirname_lower,
                        path_hint=path_hint,
                        name_hint=name_hint,
                    )

    def _on_created_legacy(
        self,
        event,
        rule: _LegacyRule,
        dirname: str | None = None,
        basename: str | None = None,
        src_lower: str | None = None,
        dirname_lower: str | None = None,
        path_hint: bool = True,
        name_hint: bool = True,
    ):
        """Legacy dispatch path for modules using input.path/input.name.

        Same matching semantics as before, but the per-event derived strings
        (dirname/basename/lowercase variants) are computed once by the caller,
        the per-rule constants (lowered suffixes, regex emptiness, '/*'
        presence) are precompiled in _LegacyRule, and the union pre-filter
        hints allow skipping per-rule regex searches that cannot match.
        """
        input_type = rule.input_type

        if input_type == "dir" and event.is_directory:
            src_path = event.src_path

            if rule.module_path not in src_path:
                path_pattern_suffix = rule.path_pattern_suffix

                if rule.is_path_regex and rule.path_regex.search(src_path):
                    logger.debug(
                        f"{rule.module_name} Directory '{src_path}' will be processed "
                        f"(regex match)"
                    )
                    self.handle_directory_event(event, rule.module_instance)

                elif (
                    path_pattern_suffix == "{case_path}"
                    and src_path == str(self.case_path)
                ):
                    logger.debug(f"{rule.module_name} Directory '{src_path}' will be processed")
                    self.handle_directory_event(event, rule.module_instance)

                elif (
                    path_pattern_suffix
                    and "{case_path}" in path_pattern_suffix
                    and src_path == path_pattern_suffix.replace("{case_path}", str(self.case_path))
                ):
                    logger.debug(f"{rule.module_name} Directory '{src_path}' will be processed")
                    self.handle_directory_event(event, rule.module_instance)

                elif (
                    path_pattern_suffix
                    and path_pattern_suffix.endswith('/*')
                    and os.path.dirname(src_path).lower().endswith(rule.wildcard_lower)
                ):
                    logger.debug(f"{rule.module_name} Directory '{src_path}' will be processed")
                    self.handle_directory_event(event, rule.module_instance)

                elif path_pattern_suffix and src_path.lower().endswith(rule.suffix_lower):
                    logger.debug(f"{rule.module_name} Directory '{src_path}' will be processed")
                    self.handle_directory_event(event, rule.module_instance)

        elif input_type == "file" and not event.is_directory:
            if dirname is None:
                dirname = os.path.dirname(event.src_path)
            if basename is None:
                basename = os.path.basename(event.src_path)
            if src_lower is None:
                src_lower = event.src_path.lower()
            if dirname_lower is None:
                dirname_lower = dirname.lower()

            if rule.module_path in dirname:
                return

            file_regex = rule.file_regex
            path_pattern_suffix = rule.path_pattern_suffix

            if rule.is_path_regex and path_hint and rule.path_regex.search(event.src_path):
                if file_regex is not None and file_regex.search(basename):
                    self._mark_and_process_legacy(event, rule)

            elif path_pattern_suffix and file_regex is not None and not rule.regex_has_pattern:
                if src_lower.endswith(rule.suffix_lower):
                    self._mark_and_process_legacy(event, rule)

            elif (
                rule.has_wildcard
                and rule.wildcard_body_lower in src_lower
                and file_regex is not None
                and file_regex.search(basename)
            ):
                self._mark_and_process_legacy(event, rule)

            elif path_pattern_suffix and rule.regex_has_pattern:
                if (
                    dirname_lower.endswith(rule.suffix_lower)
                    and file_regex.search(basename)
                ):
                    self._mark_and_process_legacy(event, rule)

            elif not path_pattern_suffix and rule.regex_has_pattern:
                if name_hint and file_regex.search(basename):
                    self._mark_and_process_legacy(event, rule)

    def _mark_and_process_legacy(self, event, rule: _LegacyRule):
        """Dedup-guarded process() for legacy file matches."""
        file_module_pair = (event.src_path, rule.module_name)
        if file_module_pair in self.last_processed:
            return
        self.last_processed.add(file_module_pair)
        self._queue_legacy_file_task_when_stable(event.src_path, rule.module_instance)

    # ------------------------------------------------------------------
    # Directory idle detection
    # ------------------------------------------------------------------

    def handle_directory_event(self, event, module_instance: OsirModuleModel):
        """
        Processes directory events that match configured patterns and sets up checks for idleness.
        """
        src_abs = os.path.abspath(event.src_path)
        if self._is_barrier_consumer(src_abs, module_instance) and self._barriers_pending():
            self._deferred[(event.src_path, module_instance.module_name)] = (event, module_instance)
            logger.debug(
                f"{module_instance.module_name} Directory '{event.src_path}' deferred: "
                f"hold_consumers barrier still active"
            )
            return

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
        if logger.isEnabledFor(10):  # logging.DEBUG
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
    # Batched file-task flush
    # ------------------------------------------------------------------

    def _hash_for_dedup(self, item: tuple[str, '_CompiledRule']):
        """Compute (path, rule, size, hash_mode, hash) for one pending file.

        Returns hash fields as None on failure; the file is then pushed
        anyway (same behavior as before: dedup failure never drops a task).
        """
        path, rule = item

        try:
            file_size = os.path.getsize(path)
        except Exception:
            file_size = -1

        try:
            if rule.module_name in self._full_hash_dedup_modules:
                return path, rule, file_size, "full", compute_file_xxh3_128_full(path)

            prefix_size = 81920
            return (
                path, rule, file_size,
                f"prefix:{prefix_size}",
                compute_file_xxh3_128_prefix(path, prefix_size=prefix_size),
            )
        except Exception as e:
            logger.warning(f"{rule.module_name} - Hash dedup failed for {path}: {e}")
            return path, rule, file_size, None, None

    def _flush_pending_file_tasks(self, wait: bool = False) -> None:
        """Hand the pending buffer to the background flush executor.

        Hashing + dedup + bulk push run on a worker thread so the scan loop
        keeps dispatching entries while previous batches are hashed/pushed.
        With wait=True, blocks until every submitted batch has completed
        (used at end of a scan pass and before exit checks).
        """
        with self._pending_lock:
            pending = self._pending_file_tasks
            self._pending_file_tasks = []

        if pending:
            future = self._flush_executor.submit(self._process_pending_batch, pending)
            with self._flush_futures_lock:
                self._flush_futures = [f for f in self._flush_futures if not f.done()]
                self._flush_futures.append(future)

        if wait:
            self._drain_flushes()

    def _drain_flushes(self) -> None:
        """Wait for all in-flight flush batches; surface their errors."""
        with self._flush_futures_lock:
            futures, self._flush_futures = self._flush_futures, []

        for future in futures:
            try:
                future.result()
            except Exception as e:
                logger.error(f"Batch flush failed: {e}")

    def _process_pending_batch(self, pending: list) -> int:
        """Hash a batch of matched files in parallel, deduplicate, then push
        the surviving tasks in one bulk operation (single DB insert + single
        AMQP producer). Returns the number of tasks pushed."""
        flush_start = time.time()

        # 1) Hashing is I/O + C-extension bound: parallelize it.
        with ThreadPoolExecutor(max_workers=self._hash_workers) as pool:
            hashed = list(pool.map(self._hash_for_dedup, pending, chunksize=8))

        hash_duration = time.time() - flush_start

        # 2) Serial dedup against the shared cache.
        to_push = []
        duplicates = 0
        duplicates_by_module: dict[str, int] = {}

        with self._seen_prefix_lock:
            for path, rule, file_size, hash_mode, file_hash in hashed:
                if file_hash is None:
                    to_push.append((path, rule))
                    continue

                key = (rule.module_name, file_size, hash_mode, file_hash)
                duplicate_of = self._seen_prefix.get(key)

                if duplicate_of is not None:
                    duplicates += 1
                    duplicates_by_module[rule.module_name] = duplicates_by_module.get(rule.module_name, 0) + 1
                else:
                    self._seen_prefix[key] = path
                    to_push.append((path, rule))

        # 3) Build payloads from the precompiled dump (no pydantic
        #    deepcopy/serialization on the hot path).
        items = []
        for path, rule in to_push:
            base = rule.base_dump
            payload = dict(base)
            payload["input"] = dict(base["input"])
            payload["input"]["match"] = path

            items.append({
                "task_name": rule.task_name,
                "queue": rule.queue,
                "module_name": rule.module_name,
                "match": path,
                "payload_json": json.dumps(payload),
                "processor_os": rule.processor_os,
            })

        # 4) Bulk DB insert + bulk publish.
        TaskService.push_tasks_bulk(
            self._case_path_norm,
            self.case_uuid,
            self.handler_uuid,
            items,
        )

        with self._task_counter_lock:
            for it in items:
                self._tasks_pushed_by_module[it["module_name"]] += 1

        duplicates_detail = ", ".join(
            f"{m}: {n}" for m, n in sorted(duplicates_by_module.items())
        ) or "none"
        logger.info(
            f"Batch flush: {len(items)} task(s) pushed, {duplicates} duplicate(s) skipped "
            f"({duplicates_detail}), "
            f"{len(pending)} candidate(s) in {time.time() - flush_start:.2f}s "
            f"(hashing: {hash_duration:.2f}s, workers: {self._hash_workers})"
        )

        return len(items)

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
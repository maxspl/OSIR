import os
import re
import shutil
from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


@osir_internal_module
class UAC_Extractor():
    """
    PyModule to perform processing operations on UAC collect.

    Handles every archive layout UAC can produce, all through a single ``7zz``
    tool (same idiom as extract_orc):
      * ``.zip`` -> extracted in one pass, using a password when the archive is encrypted
      * ``.tar.gz`` -> extracted in two passes, 7zz first strips the gzip layer
        and yields an intermediate ``.tar`` that is then extracted (same idea as
        the nested ``.7z`` handling in extract_orc)

    The command placeholders are resolved locally (``safe_format`` -> ``run`` ->
    restore), exactly like extract_orc. Custom ``{m_*}`` placeholders are used on
    purpose so that ``OsirTool.update()`` (which runs once at module construction
    and would otherwise bake ``{optional_password}`` to the YAML value) leaves them
    untouched, letting us inject the runtime password ourselves.

    The (optional) password used for encrypted zip archives is resolved from:
      1. the module ``optional.password`` (same config mechanism as extract_orc), then
      2. the sibling UAC ``.log`` file whose ``[Output Information]`` section holds
         ``Password: "..."``.
    """

    # Matches the `Password: "xxx"` line of the UAC .log side-car file.
    _LOG_PASSWORD_REX = re.compile(
        r'^\s*Password:\s*"?(?P<password>.+?)"?\s*$', re.MULTILINE
    )
    # UAC compresses its tar archives with gzip only, so the sole format whose
    # first 7zz pass leaves an intermediate .tar behind is .tar.gz.
    _COMPRESSED_TAR_SUFFIX = ".tar.gz"

    def __init__(self, case_path: str, module: OsirModule):
        """
        Initializes the Module.
        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (OsirModule): Instance of OsirModule containing configuration details for the extraction process.
        """
        self.module = module
        self._cmd = self.module.tool.cmd  # Save cmd with place holders for further iterations
        self._case_path = case_path  # Base directory for operations
        self._file_to_process = module.input.match
        self._name_rex = self.module.input.name

    def __call__(self) -> bool:
        """
        Execute the internal processor of the module
        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        try:
            logger.debug(f"Processing file {self.module.input.match}")
            archive_path = str(self._file_to_process)
            endpoint_dir = os.path.join(self._case_path, self.module.get_module_name(), "Endpoint_" + self.module.endpoint_name)
            os.makedirs(endpoint_dir, exist_ok=True)

            # Resolve the (optional) password BEFORE moving the archive: the UAC
            # .log side-car that may hold it lives next to the archive.
            password = self._resolve_password(archive_path)

            moved_archive_path = os.path.join(endpoint_dir, os.path.basename(archive_path))
            shutil.move(archive_path, moved_archive_path)
            self._move_sibling_log(archive_path, endpoint_dir)
            extraction_dir = os.path.join(endpoint_dir, "extracted_files")
            os.makedirs(extraction_dir, exist_ok=True)

            # First pass: extract the archive itself.
            self.extract(moved_archive_path, extraction_dir, password)

            # Second pass: a .tar.gz/.tgz/... yields an intermediate .tar that
            # 7zz leaves at the root of the extraction dir; extract it in turn.
            if moved_archive_path.lower().endswith(self._COMPRESSED_TAR_SUFFIX):
                self.extract_intermediate_tar(extraction_dir, password)

            # OsirTool.run() does not raise on a non-zero tool exit (e.g. wrong or
            # missing password), so make sure something was actually extracted.
            if not self._has_files(extraction_dir):
                logger.error(
                    f"Extraction produced no file from {moved_archive_path}. "
                    "For an encrypted zip, check the password (module 'optional.password' "
                    "or the sibling UAC .log file)."
                )
                return False

            self.module.input.file = moved_archive_path
            self.module.output.output_dir = extraction_dir
            logger.debug(f"{self.module.module_name} done")
            return True
        except Exception as exc:
            logger.error(f"Failed to process {self._file_to_process}: {exc}")
            return False

    def extract(self, input_file: str, output_dir: str, password) -> None:
        """
        Run the configured extraction tool (7zz) on ``input_file`` into
        ``output_dir``, filling the command place holders locally the same way
        extract_orc does (safe_format -> run -> restore the template).
        """
        replacements = {
            "m_output_dir": output_dir,
            "m_input_file": input_file,
            "m_password": password or "",
        }
        self.module.tool.cmd = self.module.tool.safe_format(self._cmd, **replacements)
        try:
            self.module.tool.run()
        finally:
            # Always restore the template (and never leave the password in tool.cmd).
            self.module.tool.cmd = self._cmd

    def extract_intermediate_tar(self, extraction_dir: str, password) -> None:
        """
        Extract the intermediate ``.tar`` produced by the first 7zz pass on a
        compressed tarball. Only top-level ``.tar`` files are considered, to
        avoid touching genuine ``*.tar`` artifacts collected deeper in the tree.
        """
        for name in os.listdir(extraction_dir):
            if not name.lower().endswith(".tar"):
                continue
            tar_path = os.path.join(extraction_dir, name)
            if not os.path.isfile(tar_path):
                continue
            try:
                self.extract(tar_path, extraction_dir, password)
                os.remove(tar_path)  # Remove the intermediate archive after extraction
            except Exception as e:
                logger.error(f"Failed to extract intermediate tar {tar_path}: {e}")

    @staticmethod
    def _has_files(directory: str) -> bool:
        """Return True if ``directory`` contains at least one file (recursively)."""
        for _root, _dirs, files in os.walk(directory):
            if files:
                return True
        return False

    def _resolve_password(self, archive_path: str):
        """
        Resolve the archive password. Precedence:
          1. explicit ``optional.password`` from the module configuration/CLI,
          2. the ``Password: "..."`` line of the sibling UAC ``.log`` file,
          3. ``None`` (archive assumed to be unencrypted).
        """
        password = self._configured_password()
        if password:
            logger.debug("Using UAC archive password from module configuration")
            return password
        return self._password_from_log(archive_path)

    def _configured_password(self):
        """Return ``optional['password']`` if provided (``optional`` is a plain dict)."""
        optional = getattr(self.module, "optional", None)
        if not optional:
            return None
        password = optional.get("password") if hasattr(optional, "get") else getattr(optional, "password", None)
        return password or None

    def _password_from_log(self, archive_path: str):
        """Extract the password from the UAC ``.log`` file sitting next to the archive."""
        log_path = self._sibling_log_path(archive_path)
        if not log_path or not os.path.isfile(log_path):
            return None
        try:
            with open(log_path, "r", errors="replace") as fh:
                content = fh.read()
        except OSError as e:
            logger.warning(f"Unable to read UAC log {log_path}: {e}")
            return None
        match = self._LOG_PASSWORD_REX.search(content)
        if match:
            password = match.group("password").strip()
            if password:
                logger.debug(f"Recovered UAC archive password from {log_path}")
                return password
        return None

    def _sibling_log_path(self, archive_path: str):
        """
        Return the path of the UAC ``.log`` side-car for ``archive_path``.
        UAC names it exactly like the archive with a ``.log`` extension, e.g.
        ``uac-host-linux-<ts>.zip`` -> ``uac-host-linux-<ts>.log``.
        """
        lower = archive_path.lower()
        # Match .tar.gz before .tar so the whole double extension is stripped.
        for suffix in (".zip", ".tar.gz", ".tar"):
            if lower.endswith(suffix):
                return archive_path[: len(archive_path) - len(suffix)] + ".log"
        return os.path.splitext(archive_path)[0] + ".log"

    def _move_sibling_log(self, archive_path: str, endpoint_dir: str) -> None:
        """Move the UAC ``.log`` side-car (if any) next to the archive in ``endpoint_dir``."""
        log_path = self._sibling_log_path(archive_path)
        if not log_path or not os.path.isfile(log_path):
            return
        try:
            shutil.move(log_path, os.path.join(endpoint_dir, os.path.basename(log_path)))
            logger.debug(f"Moved UAC log {os.path.basename(log_path)} to {endpoint_dir}")
        except OSError as e:
            logger.warning(f"Failed to move UAC log {log_path}: {e}")
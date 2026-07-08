import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


@osir_internal_module
class InjectionModule():
    """Index module output into Splunk via json2splunk-rs.

    Builds a {output_dir: [modules]} map from the module configs, then indexes
    whatever the target points to (the whole case, a folder, or a single file).
    json2splunk-rs uses --input for both directories and single files.
    The Splunk index name comes from the case root.
    """

    def __init__(self, module: OsirModule):
        self.module = module
        self.case_root: Optional[Path] = Path(module.case_path).resolve() if module.case_path else None
        self.target: Optional[Path] = (
            Path(module.input.match) if module.input.match else self.case_root
        )
        self.output_map: Dict[Path, List[Tuple[str, str]]] = {}

    def __call__(self) -> bool:
        try:
            if self.target is None:
                logger.error("indexer_ng: no target and no case_path set.")
                return False

            target = self.target.resolve()
            case_root = (self.case_root or target).resolve()

            if not target.exists():
                logger.error(f"indexer_ng: target does not exist: '{target}'")
                return False

            self.output_map = self._build_output_map(case_root)
            if not self.output_map:
                logger.warning("indexer_ng: no splunk-enabled module found.")
                return True

            if target.is_file():
                self._index_file(target)
            else:
                self._index_dir(target)

            logger.debug(f"{self.module.module_name} done")
            return True

        except Exception as exc:
            logger.error_handler(exc)
            return False

    # mapping of module yml files (only if they contain splunk section)
    def _build_output_map(self, case_root: Path) -> Dict[Path, List[Tuple[str, str]]]:
        """Map each output directory to the module(s) writing there.

        Several modules can share the same output directory for Splunk ingestion,
        e.g. "{case_path}/live_response/packages".
        """
        out_map: Dict[Path, List[Tuple[str, str]]] = {}

        for rel in FileManager.get_yaml_files(OSIR_PATHS.MODULES_DIR, relative=True):
            yaml_path = os.path.join(OSIR_PATHS.MODULES_DIR, rel)

            try:
                model = OsirModuleModel.from_yaml(yaml_path)
            except Exception as exc:
                logger.debug(f"indexer_ng: skipping unreadable module '{rel}': {exc}")
                continue

            if not model.splunk:
                continue

            output_dir = self._resolve_output_dir(model, case_root)
            if output_dir is not None:
                out_map.setdefault(output_dir, []).append((model.module_name, yaml_path))

        return out_map

    @staticmethod
    def _resolve_output_dir(model: OsirModuleModel, case_root: Path) -> Optional[Path]:
        """Return the directory where this module writes its output.

        - No output_dir in the YAML -> <case>/<module>
        - output_dir set            -> resolved path with {case_path} and {module}

        If the path still contains another placeholder, it cannot be resolved here.
        """
        out = model.output.output_dir if model.output else None
        module_name = model.module_name

        if not out:
            return (case_root / module_name).resolve()

        if "{case_path}" in out:
            resolved = out.replace("{case_path}", str(case_root)).replace("{module}", module_name)
        else:
            resolved = str(case_root / module_name / out).replace("{module}", module_name)

        if "{" in resolved:
            logger.warning(
                f"indexer_ng: module '{module_name}': unresolved placeholder in "
                f"output_dir '{out}' — skipped."
            )
            return None

        return Path(resolved).resolve()

    def _index_dir(self, dir_path: Path) -> None:
        """Index a folder: either an output directory itself, or a parent folder
        holding several output directories."""
        dir_path = dir_path.resolve()

        if dir_path in self.output_map:
            for module_name, yaml_path in self.output_map[dir_path]:
                self._run(dir_path, yaml_path, module_name)
            return

        ran = False

        for output_dir, modules in self.output_map.items():
            if output_dir.exists() and self._is_within(output_dir, dir_path):
                for module_name, yaml_path in modules:
                    self._run(output_dir, yaml_path, module_name)
                ran = True

        if not ran:
            logger.warning(f"indexer_ng: '{dir_path}' matches no module output directory.")

    def _index_file(self, file_path: Path) -> None:
        """Index a single file with the patterns of its directory's module(s)."""
        file_path = file_path.resolve()
        modules = self.output_map.get(file_path.parent.resolve())

        if not modules:
            logger.warning(f"indexer_ng: file '{file_path}' is not under a known output directory.")
            return

        for module_name, yaml_path in modules:
            self._run(file_path, yaml_path, module_name)

    def _run(self, input_path: Path, yaml_path: str, module_name: str) -> None:
        """Run json2splunk-rs on one input with one module's patterns.
        """
        replacements = {
            "indexer_path": yaml_path,
            "input_dir_replaced_by_internal_module": str(input_path),
        }

        original_cmd = self.module.tool.cmd

        try:
            self.module.tool.cmd = self.module.tool.safe_format(
                self.module.tool.cmd,
                **replacements,
            )

            input_kind = "file" if input_path.is_file() else "dir"
            logger.info(
                f"indexer_ng: indexing {input_kind} '{input_path}' "
                f"with patterns of '{module_name}'."
            )

            self.module.tool.run()

        finally:
            self.module.tool.cmd = original_cmd

    @staticmethod
    def _is_within(child: Path, parent: Path) -> bool:
        """True if child is somewhere under parent."""
        try:
            return parent.resolve() in child.resolve().parents
        except Exception:
            return False
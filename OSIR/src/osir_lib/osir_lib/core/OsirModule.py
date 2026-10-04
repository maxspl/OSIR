from pathlib import Path
import re
from typing import Optional
from pydantic import model_validator
from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_lib.core.model.OsirOutputModel import OsirOutputModel
from osir_lib.core.model.OsirInputModel import OsirInputModel
from osir_lib.core.model.OsirToolModel import OsirToolModel
from osir_lib.core.OsirInput import OsirInput
from osir_lib.core.OsirOutput import OsirOutput
from osir_lib.core.OsirTool import OsirTool
from osir_lib.core.OsirPathTransformerMixin import OsirPathTransformerMixin
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()


class OsirModule(OsirModuleModel):
    """
        Main domain class representing a forensic processing module within OSIR.

        Attributes:
            case_path (Path): The filesystem path to the current forensic case.
            tool (OsirTool): The forensic tool/binary logic associated with this module.
            input (OsirInput): The source file or data to be processed.
            output (OsirOutput): The destination and formatting logic for results.
            extracted_values (dict): Every value declared under the `extracted`
                section, keyed by extraction name. Each one is exposed as an
                `{extracted_<name>}` placeholder in tool, output and splunk
                constant templates.
            endpoint_name (str): Shortcut to the `endpoint` extraction.
            user_name (str): Shortcut to the `user` extraction.
    """
    case_path: Path = None
    _module_filepath: Optional[str] = None
    tool: Optional[OsirTool] = None
    input: Optional[OsirInput] = None
    output: Optional[OsirOutput] = None
    extracted_values: Optional[dict] = None
    endpoint_name: Optional[str] = None
    user_name: Optional[str] = None

    @property
    def extracted_placeholders(self) -> dict:
        """The extracted values as template replacements: every extraction
        named X is exposed as `{extracted_X}`."""
        return {
            f"extracted_{name}": value
            for name, value in (self.extracted_values or {}).items()
        }

    def __init__(self, **data):
        """
            Initializes the OsirModule by converting base models module into OsirModule.
        """
        super().__init__(**data)
        self._module_filepath = FileManager.get_module_path(self.module_name)

        if isinstance(self.output, OsirOutputModel):
            self.output = OsirOutput(**self.output.model_dump())
        if isinstance(self.tool, OsirToolModel):
            self.tool = OsirTool(**self.tool.model_dump())
            if self.env:
                self.tool.env = self.env
            self.tool.init_tool(self.configuration.processor_os)
        if isinstance(self.input, OsirInputModel):
            self.input = OsirInput(**self.input.model_dump())

    @model_validator(mode='after')
    def link_and_update(self) -> 'OsirModule':
        """
            Post-initialization validator that establishes component relationships.

            Returns:
                OsirModule: The fully linked and updated module instance.
        """
        extracted_values = self._extract_values()
        self.extracted_values = extracted_values
        self.endpoint_name = extracted_values.get('endpoint', 'UNKNOWN')
        self.user_name = extracted_values.get('user', 'UNKNOWN_USER')

        for child in [self.input, self.output]:
            if child:
                child._context = self

        if self.input and hasattr(self.input, 'update'):
            self.input.update()

        if self.output and hasattr(self.output, 'update'):
            self.output.update()

        if self.tool and hasattr(self.tool, 'update'):
            self.tool._context = self
            self.tool.update()

        self._update_splunk_constants()

        return self

    def _extract_values(self) -> dict:
        """
            Runs every extraction declared under `extracted` against the
            input path: patterns are tried in order (first capture group
            wins), `default` is the fallback.

        Returns:
            dict: The extracted values, keyed by extraction name.
        """
        values: dict = {}

        if not self.extracted or not self.input or not self.input.match:
            return values

        input_match_str = str(self.input.match)

        for entry in self.extracted:
            values[entry.name] = self._extract_value(entry, input_match_str)

        return values

    @staticmethod
    def _extract_value(entry, input_match_str: str) -> str:
        """
            Extracts one named value from the input path.

        Args:
            entry (OsirExtractedEntry): The extraction entry (name,
                patterns, default).
            input_match_str (str): The input path to match against.

        Returns:
            str: The first capture group of the first matching pattern,
            or the entry default.
        """
        if not entry.patterns:
            return entry.default or 'UNKNOWN'

        try:
            for pattern in entry.patterns:
                if pattern.startswith(('r"', "r'")):
                    pattern = pattern[2:-1]

                match = re.search(pattern, input_match_str)

                if match and match.groups():
                    return match.group(1)

        except Exception as e:
            logger.error(f"Error extracting {entry.name}: {e}")

        return entry.default or 'UNKNOWN'

    def _update_splunk_constants(self) -> None:
        """
            Resolves the `constant` maps of the splunk configuration the
            same way tool and output templates are resolved: every
            placeholder — including the `{extracted_<name>}` values — is
            substituted with the runtime values.
        """
        if not self.splunk:
            return

        replacements = {
            "input_file": str(self.input.match_updated) if self.input else "",
            "input_dir": str(self.input.match_updated) if self.input else "",
            "output_dir": str(self.output.output_dir) if self.output else "",
            "output_file": str(self.output.output_file) if self.output else "",
            "output_filename": str(self.output.filename) if self.output else "",
            "case_name": self.case_name,
            "case_path": str(self.case_path) if self.case_path else "",
            **self.extracted_placeholders,
        }

        for params in self.splunk.values():
            if not isinstance(params, dict):
                continue
            constants = params.get('constant') or params.get('constants')
            if not isinstance(constants, dict):
                continue
            for key, value in constants.items():
                if isinstance(value, str):
                    constants[key] = OsirPathTransformerMixin.safe_format(value, **replacements)

    @model_validator(mode='after')
    def validate_module_if_internal(self) -> 'OsirModuleModel':
        """
            Ensures internal Python-based modules are discoverable and valid.

            Raises:
                ValueError: If the internal module logic cannot be loaded.
        """
        if "internal" in self.configuration.processor_type:
            if self.configuration.alt_module:
                if self.find_and_load_internal_module(self.configuration.alt_module):
                    return self

            if not self.find_and_load_internal_module():
                raise ValueError(
                    f"The module '{self.configuration.module}' could not be found or does not "
                    f"contain a valid PyModule class within {OSIR_PATHS.PY_MODULES_DIR}."
                )
        return self

    @property
    def output_dir(self) -> str:
        """
            Constructs the absolute path where the module results will be stored.

            Returns:
                str: The joined path as a string, or empty if no case_path is set.
        """
        if not self.case_path:
            return ""

        return str(Path(self.case_path) / self.configuration.module)

    @property
    def module(self) -> str:
        return self.configuration.module

    @property
    def case_name(self) -> str:
        """
            Extracts the identifier of the current case from the filesystem path.

            Returns:
                str: The lowercase name of the case directory.
        """
        if not self.case_path:
            return ""

        return Path(self.case_path).name.lower()

    @property
    def is_wsl(self):
        """
            Runtime detection for the Windows Subsystem for Linux environment.

            Returns:
                bool: True if executing inside WSL, False otherwise.
        """
        try:
            with open('/proc/sys/kernel/osrelease', 'rt') as f:
                return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
        except FileNotFoundError:
            pass

        try:
            with open('/proc/version', 'rt') as f:
                return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
        except FileNotFoundError:
            return False


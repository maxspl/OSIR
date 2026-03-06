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
from osir_lib.core.model.connector.OsirConnectorModel import OsirConnectorModel

from osir_lib.core.OsirInput import OsirInput
from osir_lib.core.OsirOutput import OsirOutput
from osir_lib.core.OsirTool import OsirTool
from osir_lib.core.OsirConnector import OsirConnector
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
            endpoint_name (str): The name of the workstation or source of the artifact.
    """
    case_path: Path = None
    _module_filepath: Optional[str] = None
    tool: Optional[OsirTool] = None
    input: Optional[OsirInput] = None
    output: Optional[OsirOutput] = None
    connector: Optional[OsirConnector] = None
    endpoint_name: Optional[str] = None

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
        if isinstance(self.connector, OsirConnectorModel):
            self.connector = OsirConnector(**self.connector.model_dump())

    @model_validator(mode='after')
    def link_and_update(self) -> 'OsirModule':
        """
            Post-initialization validator that establishes component relationships.

            Returns:
                OsirModule: The fully linked and updated module instance.
        """
        self.endpoint_name = self._calculate_endpoint_name()

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

        return self

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

    def _calculate_endpoint_name(self) -> str:
        """
            Parse the input file path (or other match string) to extract the originating
            endpoint/hostname using a fallback regex strategy.

            Returns:
                str: The extracted endpoint/hostname if found, otherwise "UNKNOWN".
        """
        if not self.endpoint or not self.input or not self.input.match:
            return 'UNKNOWN'

        if not self.endpoint.patterns:
            return self.endpoint.default
        
        input_match_str = str(self.input.match)

        try:
            for pattern in self.endpoint.patterns:
                if pattern.startswith(('r"', "r'")):
                    pattern = pattern[2:-1]

                endpoint_match = re.search(pattern, input_match_str)

                if endpoint_match and endpoint_match.groups():
                    return endpoint_match.group(1)

        except Exception as e:
            logger.error(f"Error extracting endpoint: {e}")
        
        if self.endpoint.default:
            return self.endpoint.default
        else:
            return "UNKNOWN"
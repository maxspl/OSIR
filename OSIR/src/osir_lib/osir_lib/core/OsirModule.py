from pathlib import Path
import pprint
import re
from typing import Optional

from pydantic import computed_field, model_validator
from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirAgentConfig import OsirAgentConfig
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
        Domain class extending OsirModuleModel.
        Automatically replaces nested models by their domain equivalents.
    """
    case_path: Path = None
    _module_filepath: Optional[str] = None
    tool: Optional[OsirTool] = None        
    input: Optional[OsirInput] = None     
    output: Optional[OsirOutput] = None   
    connector: Optional[OsirConnector] = None
    endpoint_name: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        self._module_filepath = FileManager.get_module_path(self.module_name)

        if isinstance(self.output, OsirOutputModel):
            self.output = OsirOutput(**self.output.model_dump())
        if isinstance(self.tool, OsirToolModel):
            self.tool = OsirTool(**self.tool.model_dump())
            if self.env:
                self.tool.env = self.env
            self.tool.init_tool(self.processor_os)
        if isinstance(self.input, OsirInputModel):
            self.input = OsirInput(**self.input.model_dump())
        if isinstance(self.connector, OsirConnectorModel):
            self.connector = OsirConnector(**self.connector.model_dump())

    @model_validator(mode='after')
    def link_and_update(self) -> 'OsirModule':
        
        self.endpoint_name = self._calculate_endpoint_name()

        for child in [self.input, self.output]:
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
        Pydantic validator to ensure the 'module' exists and is valid 
        when the processor_type includes 'internal'.
        """
        
        if "internal" in self.processor_type:
            if self.alt_module:
                if self.find_and_load_internal_module(self.alt_module):
                    return self
                
            if not self.find_and_load_internal_module():
                raise ValueError(
                    f"The module '{self.module}' could not be found or does not "
                    f"contain a valid PyModule class within {OSIR_PATHS.PY_MODULES_DIR}."
                )
        return self
        
    @property
    def output_dir(self) -> str:
        """
        Calculates the output directory: case_path / module_name.
        Returns an empty string if case_path is not set.
        """
        if not self.case_path:
            return ""
        
        # Le slash '/' est l'opérateur de jonction de pathlib
        return str(Path(self.case_path) / self.module)

    @property
    def case_name(self) -> str:
        """
        Returns the name of the directory (basename) in lowercase.
        """
        if not self.case_path:
            return ""
            
        # .name récupère le dernier composant du chemin (équivalent basename)
        return Path(self.case_path).name.lower()

    @property
    def is_wsl(self):
        """
        Checks if the script is running inside Windows Subsystem for Linux (WSL).

        Returns:
            bool: True if running inside WSL, False otherwise.
        """
        """Check if running inside WSL."""
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
        """La vraie logique de calcul, sans décorateur Pydantic gênant pour l'interne."""
        if not self.endpoint or not self.input or not self.input.match: 
            return 'UNKNOWN'
        try:
            input_match_str = str(self.input.match)
            # Utilisation de re.search avec le pattern
            endpoint_match = re.search(self.endpoint, input_match_str)
            if endpoint_match and endpoint_match.groups():
                return endpoint_match.group(1)
        except Exception as e:
            logger.error(f"Error extracting endpoint: {e}")
        return 'UNKNOWN'
    
from typing import Optional
from osir_lib.core.FileManager import FileManager
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

    module_name: Optional[str] = None
    _module_filepath: Optional[str] = None
    tool: Optional[OsirTool] = None        
    input: Optional[OsirInput] = None     
    output: Optional[OsirOutput] = None   
    connector: Optional[OsirConnector] = None

    def __init__(self, **data):
        super().__init__(**data)

        # -------- AUTO-CONVERSIONS OF NESTED MODELS -------- #
        self.module_name = self.module
        self._module_filepath = FileManager.get_module_path(self.module_name)
        if isinstance(self.tool, OsirToolModel):
            self.tool = OsirTool(**self.tool.model_dump())
            if self.env:
                self.tool.env = self.env
            self.tool.init_tool(self.processor_os)
        if isinstance(self.input, OsirInputModel):
            self.input = OsirInput(**self.input.model_dump())
        if isinstance(self.output, OsirOutputModel):
            self.output = OsirOutput(**self.output.model_dump())
        if isinstance(self.connector, OsirConnectorModel):
            self.connector = OsirConnector(**self.connector.model_dump())
    
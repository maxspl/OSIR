import os
from pathlib import Path, PureWindowsPath
import shutil
from osir_lib.core import StaticVars
from osir_lib.core.model.OsirToolModel import OsirToolModel

from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

class OsirTool(OsirToolModel):
    def __init__():
        super()

    def init_tool(self, processor_os):
        """
        
        Retrieves detailed information about the tool used by the module, if configured, including path, command,
        source, and version. Paths are resolved based on operating system compatibility.

        """
        
        bin_dir = StaticVars.TOOL_DIR

        tool_path = None  # Default to None if no valid path is found

        if processor_os == "unix":
            potential_path = os.path.join(bin_dir, self.path)
            if os.path.exists(potential_path):
                tool_path = potential_path
            elif shutil.which(self.path):  # Check if the tool is in the system PATH
                tool_path = shutil.which(self.path)
            elif os.path.exists(self.path):  # Check if the provided full path exists
                tool_path = self.path

        elif processor_os == "windows":
            tool_path = os.path.join("{drive}\\OSIR\\bin", self.path)
            tool_path = str(PureWindowsPath(Path(tool_path)))  # Convert path to windows

        if tool_path is None:
            logger.error(f"Tool binary not found in bin_dir, system PATH, or provided full path: {self.path}")

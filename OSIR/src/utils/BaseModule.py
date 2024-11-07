import subprocess
from typing import Any
import yaml
import os
import shutil
from pathlib import Path, PureWindowsPath
import winrm
from src.utils.AgentConfig import AgentConfig
import requests.exceptions
import time
import uuid
from src.log.logger_config import AppLogger

logger = AppLogger(__name__).get_logger()

# TODO ENV FILE
DIR_RESULT = "../../../share/fifos/result/"
DIR_EXECUTOR = "../../../share/fifos/execute/"

MAX_RETRIES = 60
RETRY_DELAY = 2  # in seconds


class BaseTool():
    """
    Handles operations for different tools by executing commands both locally and remotely.
    """
    # tool:
    #   path: 7zz
    #   source:
    #   version: 22.01
    #   cmd: x -o{output_dir} -y {input_file} -p{optional_password}
    def __init__(self, tool_data: dict, env: list) -> None:
        """
        Initializes the tool with its specific data and environment settings.

        Args:
            tool_data (dict): Data containing path, version, command, and source of the tool.
            env (List[str]): Environment variables for tool execution.
        """
        self.path: str = tool_data.get('path', '')
        self.version: str = tool_data.get('version', '')
        self.cmd: str = tool_data.get('cmd', '')
        self.source: str = tool_data.get('source', '')
        self.env = env

    def run_remote(self):
        """
        Executes the tool command remotely via WinRM.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating success, and output or error message.
        """
        try:
            cmd = self.path + ' ' + self.cmd
            agent_config = AgentConfig()
            logger.debug(f"running WinRM cmd : {cmd}")
            session = winrm.Session(agent_config.windows_host, auth=(agent_config.windows_user, agent_config.windows_password))
            r = session.run_ps(cmd)
            std_out = str(r.std_out).replace('\\n', '\n')
            std_err = str(r.std_err).replace('\\n', '\n')
            if r.status_code == 0:
                logger.debug(f"cmd stdout : {std_out}")
                logger.debug(f"cmd stderr : {std_err}")
                return True, r.std_out + r.std_err
            else:
                logger.debug(f"cmd stderr : {std_err}")
                return False, r.std_err

        except requests.exceptions.ConnectionError:
            logger.error("Connection refused error occurred. Please check the connection settings.")
            return False, "Connection refused error occurred. Please check the connection settings."

        except Exception as e:
            logger.error(f"Unidentified error: Error : {str(e)}")
            return False, f"Unidentified error: Error : {str(e)}"

    def run_local(self, is_agent=False, timeout=3600) -> bool:
        """
        Executes the tool command locally.

        Args:
            is_agent (bool): Specifies whether the command is run in an agent context.
            timeout (int): Maximum time in seconds before the command times out.

        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple containing the command's stdout and stderr.
        """
        try:
            logger.debug(f"Executing command: {self.path} {self.cmd}")
            env = self.update_env()
            output = subprocess.run(self.path + " " + self.cmd, shell=True, capture_output=True, timeout=timeout, text=True, env=env)
            logger.debug(f"cmd output : {output.stdout}")
            if output.stderr != "":
                logger.error(f"Something went wrong. output.stderr : {output.stderr}")
            return output.stdout, output.stderr

        except subprocess.TimeoutExpired:
            logger.error(f"Command {self.path} {self.cmd} timed out after {timeout} seconds.")
            return None, None

        except Exception as e:
            logger.error(f"Failed to run local command {self.path} {self.cmd}. Error: {str(e)}")
            return None, None

    def run_wsl_bak(self):
        """
        Placeholder function for future WSL command execution implementation.
        """
        directory = os.path.dirname(__file__)  # Gets the directory of the current script
        absolute_path_execute = os.path.abspath(os.path.join(directory, '..', '..', '..', 'share', 'fifos', 'execute'))  # Converts to absolute path
        absolute_path_result = os.path.abspath(os.path.join(directory, '..', '..', '..', 'share', 'fifos', 'result'))  # Converts to absolute path

        command = self.path + ' ' + self.cmd
        _uuid = uuid.uuid4().__str__()
        execute_path = os.path.join(absolute_path_execute, _uuid)
        result_path = os.path.join(absolute_path_result, _uuid)
        logger.debug("Execution de la commande " + command)

        os.mkfifo(execute_path)
        with open(execute_path, 'a') as command_pipe:
            command_pipe.write(command + '\n')

        retries = 0
        while retries < MAX_RETRIES:
            if os.path.exists(result_path):
                try:
                    with open(result_path, 'r') as result_pipe:
                        result = result_pipe.read().strip()
                    os.remove(result_path)
                    logger.debug(f"Resultat de la commande: {result}")
                    break  # Exit the loop if the file is successfully read and removed
                except OSError as e:
                    logger.error(f"Error reading or deleting result: {e}")
            else:
                logger.warning(f"File not found: {result_path}, retrying in {RETRY_DELAY} seconds...")
            retries += 1
            time.sleep(RETRY_DELAY)

        if retries == MAX_RETRIES:
            logger.error("Maximum retries reached. File was not found or could not be read.")
        return result

    def run_wsl(self, timeout=3600):
        """
        Placeholder function for future WSL command execution implementation.
        """
        
        try:
            command = self.path + ' ' + self.cmd
            command = f"/mnt/c/Windows/System32/WindowsPowerShell/v1.0//powershell.exe -c '{command}'"
            # command = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0//powershell.exe -c 'C:\\OSIR\\bin\\net6\\PECmd.exe -d \"\\\\wsl.localhost\\Ubuntu-22.04\\opt\\OSIR_wsl\\OSIR\\share\\cases\\INV1\\restore_fs\\DESKTOP-DA07CRI\\C\\Windows\\Prefetch\" --json \"\\\\wsl.localhost\\Ubuntu-22.04\\opt\\OSIR_wsl\\OSIR\\share\\cases\\INV1\\prefetch\" --jsonf \"DESKTOP-DA07CRI--prefetch.jsonl\" -q'"
            env = self.update_env()
            output = subprocess.run(command, shell=True, capture_output=True, timeout=timeout, text=True, env=env)
            logger.debug(f"cmd output : {output.stdout}")
            if output.stderr != "":
                logger.error(f"Something went wrong. output.stderr : {output.stderr}")
            return output.stdout, output.stderr

        except subprocess.TimeoutExpired:
            logger.error(f"Command {self.path} {self.cmd} timed out after {timeout} seconds.")
            return None, None

        except Exception as e:
            logger.error(f"Failed to run local command {self.path} {self.cmd}. Error: {str(e)}")
            return None, None
    
    def transform_cmd(self, is_agent):
        """
        Placeholder function for transforming the command based on agent context.
        """
        pass

    def update_env(self):
        """
        Updates the environment variables for the tool command execution.

        Returns:
            dict: A dictionary containing the updated environment variables.
        """
        my_env = os.environ.copy()
        for env_var in self.env:
            var_name = env_var.split("=")[0]
            var_value = env_var.split("=")[1]
            my_env[var_name] = var_value
        return my_env


class BaseInput():
    # input:
    #   type: file
    #   name: ^DFIR-ORC_(?:Server|WorkStation|DomainController)_((?:\w|-)+)_(\w+)\.7z
    def __init__(self, input_data: dict) -> None:
        self.type: str = input_data.get('type', '')
        self.name: str = input_data.get('name', '')
        self.path: str = input_data.get('path', '')
        self.file: str = ''
        self.dir: str = ''


class BaseOutput():
    """
    Manages configuration for output, including handling multiple file types and formats.
    """
    # output:
    #   type: multiples_files
    #   format: raw
    def __init__(self, output_data: dict) -> None:
        """
        Initializes output settings based on provided configuration data.

        Args:
            output_data (Dict[str, Any]): Configuration data including type, format, directory, filename, and prefix.
        """
        self.type: str = output_data.get('type', '')
        self.format: str = output_data.get('format', '')
        self.output_dir: str = output_data.get('output_dir', '')
        self.output_file: str = output_data.get('output_file', '')
        self.output_prefix: str = output_data.get('output_prefix', '')


class BaseModule():
    """
    Represents a module that can process data according to specified configurations and tools.
    """
    # version: 1.0
    # author:
    # module: extract_orc
    # description:
    # os: windows
    # type: pre-process
    # disk_only: True
    # no_multithread: True
    # processor_type:
    #   - internal
    #   - external
    # processor_os: unix
    # tool:
    #   path: 7zz
    #   source:
    #   version: 22.01
    #   cmd: x -o{output_dir} -y {input_file} -p{optional_password}
    # input:
    #   type: file
    #   name: ^DFIR-ORC_(?:Server|WorkStation|DomainController)_((?:\w|-)+)_(\w+)\.7z
    # output:
    #   type: multiples_files
    #   format: raw
    # optional:
    #   password: avproof

    def __init__(self, module_name: str) -> None:
        """
        Loads and validates a module configuration from YAML files based on the provided module name.

        Args:
            module_name (str): The name or identifier of the module to load.

        Raises:
            FileNotFoundError: If the module configuration file does not exist.
        """
        self._filename = module_name if module_name.endswith('.yml') else module_name + '.yml'

        self._module_filepath = self._validate()  # Validate now returns the full path if file exists
        data: dict = self._get_data()
        self.data = self._get_data()
        if not self.data:
            raise FileNotFoundError("The module don't follow the attended format.")
        
        if os.path.exists(self._module_filepath):
            self.version: str = data.get('version', 'Unknown version')
            self.author: str = data.get('author', 'Unknown author')
            self.module_name: str = data.get('module', 'No module name available')
            self.description: str = data.get('description', 'No description available')
            self.os: str = data.get('os', 'Unknown OS')
            self.type: str = data.get('type', 'Unknown type')
            self.requirements: list[str] = data.get('requirements', []) or []
            self.disk_only: bool = data.get('disk_only', False)
            self.no_multithread: bool = data.get('no_multithread', False)
            self.processor_type: list[str] = data.get('processor_type', []) or []
            self.processor_os: str = data.get('processor_os', 'Unknown processor os')
            self.input = BaseInput(data.get('input')) if 'input' in data else BaseInput()
            self.output = BaseOutput(data.get('output')) if 'output' in data else BaseOutput()
            self.env: str = data.get('env', '')
            self.optional: dict = data.get('optional') if 'optional' in data else ''
            self.endpoint: str = data.get('endpoint') if 'endpoint' in data else ''
        else:
            raise FileNotFoundError(f"No module found with name {self._filename} in directory {self._filepath}")

    def init_tool(self):
        self.tool = BaseTool(self._get_tool_details(), self.env) if 'tool' in self.data else BaseTool({}, [])

    def _validate(self):
        """
        Checks if the module file exists by searching recursively within the 'configs/modules/' directory.

        Returns:
            str: The path to the module file if found.

        Raises:
            FileNotFoundError: If no module file is found.
        """
        directory = os.path.dirname(__file__)  # Gets the directory of the current script
        relative_path = os.path.join(directory, '..', '..', 'configs', 'modules')
        absolute_path = os.path.abspath(relative_path)  # Converts to absolute path
        modules_dir = absolute_path
        if os.path.exists(os.path.join(relative_path, self._filename)):
            return os.path.join(relative_path, self._filename)
        for root, dirs, files in os.walk(modules_dir):
            for file in files:
                if file == self._filename:
                    return os.path.join(root, file)
        logger.error(f"No module found with name {self._filename} in directory {modules_dir}")
        raise FileNotFoundError(f"No module found with name {self._filename} in directory {modules_dir}")

    def _get_data(self) -> Any:
        """
        Loads the module data from a YAML file.

        Returns:
            Dict[str, Any]: The data loaded from the YAML file.

        Raises:
            Exception: If the file could not be loaded.
        """
        try:
            return yaml.load(open(os.path.abspath(self._module_filepath)), Loader=yaml.FullLoader)
        except Exception as e:
            logger.error("Failed to load module. Error: " + str(e))

    def _get_version(self):
        """
        Retrieves the version information of the module.

        Returns:
            str: The version of the module.
        """
        return self.version

    def get_author(self):
        """
        Retrieves the author of the module.

        Returns:
            str: The author's name.
        """
        return self.author

    def get_module_name(self):
        """
        Retrieves the name of the module.

        Returns:
            str: The module name.
        """
        return self.module_name

    def get_description(self):
        """
        Retrieves the description of the module.

        Returns:
            str: The description of the module.
        """
        return self.description

    def get_os(self):
        """
        Retrieves the operating system for which the module is designed.

        Returns:
            str: The operating system name.
        """
        return self.os

    def get_type(self):
        """
        Retrieves the type of the module.

        Returns:
            str: The type of the module.
        """
        return self.type

    def get_requirements(self):
        """
        Retrieves the requirements for the module. Each requirement is ensured to end with '.yml'.

        Returns:
            List[str]: A list of requirements, each formatted with a '.yml' extension.
        """
        requirements = self.requirements

        # Check if 'Requirements' is a string and process accordingly
        if isinstance(requirements, str):
            # Append ".yml" if it does not already end with ".yml"
            return requirements + '.yml' if not requirements.endswith('.yml') else requirements
        elif isinstance(requirements, list):
            # Append ".yml" to each element in the list if it does not already end with ".yml"
            return [req + '.yml' if not req.endswith('.yml') else req for req in requirements]
        else:
            # Return an empty list if 'Requirements' is neither a list nor a string
            return []

    def get_processor_type(self):
        """
        Retrieves the types of processors that the module can utilize.

        Returns:
            List[str]: A list of processor types (e.g., 'internal', 'external').
        """
        return self.processor_type

    def get_processor_os(self):
        """
        Retrieves the operating system type that is compatible with the processor used by the module.

        Returns:
            str: The processor's operating system type.
        """
        return self.processor_os

    def get_disk_only(self):
        """
        Checks if the module operates only on disk without requiring multithreading support.

        Returns:
            bool: True if the module requires disk access only, False otherwise.
        """
        return self.disk_only

    def get_no_multithread(self):
        """
        Determines if the module is designed to operate without multithreading.

        Returns:
            bool: True if the module does not support multithreading, False otherwise.
        """
        return self.no_multithread

    def _get_tool_details(self):
        """
        Retrieves detailed information about the tool used by the module, if configured, including path, command,
        source, and version. Paths are resolved based on operating system compatibility.

        Returns:
            dict: A dictionary containing the resolved tool path, command, source URL, and version.
        """
        directory = os.path.dirname(__file__)  # Gets the directory of the current script
        relative_path = os.path.join(directory, '..', '..', 'bin')
        absolute_path = os.path.abspath(relative_path)  # Converts to absolute path
        bin_dir = absolute_path
        tool = self.data.get('tool', {})

        tool_path = None  # Default to None if no valid path is found
        tool_config_path = tool.get('path', '')

        if self.get_processor_os() == "unix":
            potential_path = os.path.join(bin_dir, tool_config_path)
            if os.path.exists(potential_path):
                tool_path = potential_path
            elif shutil.which(tool_config_path):  # Check if the tool is in the system PATH
                tool_path = shutil.which(tool_config_path)
            elif os.path.exists(tool_config_path):  # Check if the provided full path exists
                tool_path = tool_config_path

        elif self.get_processor_os() == "windows":
            tool_config_path = tool.get('path', '')
            tool_path = os.path.join("{drive}\\OSIR\\bin", tool_config_path)
            tool_path = str(PureWindowsPath(Path(tool_path)))  # Convert path to windows

        if tool_path is None:
            logger.error(f"Tool binary not found in bin_dir, system PATH, or provided full path: {tool_config_path}")

        return {
            'path': tool_path,
            'cmd': tool.get('cmd', ''),
            'source': tool.get('source', ''),
            'version': tool.get('version', '')
        }

    def get_input_details(self) -> "BaseInput":
        """
        Retrieves input configuration details for the module, which define how input data should be handled.

        Returns:
            dict: A dictionary representing the input configuration details.
        """
        return self.input.__dict__

    def get_output_details(self) -> dict[str, Any]:
        """
        Retrieves output configuration details for the module, which define how the output should be formatted and stored.

        Returns:
            dict: A dictionary representing the output configuration details.
        """
        return self.output.__dict__

    def get_env(self):
        """
        Retrieves the environment variable settings specific to the module's operation.

        Returns:
            list: A list of environment variable strings, typically in 'KEY=VALUE' format.
        """
        return self.env

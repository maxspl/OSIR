import os
import shutil
import subprocess
import time
import uuid

import requests
import winrm 

from pathlib import Path, PureWindowsPath

from osir_lib.core import StaticVars
from osir_lib.core.model.OsirToolModel import OsirToolModel
from osir_lib.core.AgentConfig import AgentConfig

from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

# TODO ENV FILE
DIR_RESULT = "../../../share/fifos/result/"
DIR_EXECUTOR = "../../../share/fifos/execute/"

MAX_RETRIES = 60
RETRY_DELAY = 2  # in seconds


class OsirTool(OsirToolModel):
    def __init__(self, **data):
        super().__init__(**data)

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
        if self.env:
            my_env = os.environ.copy()
            for env_var in self.env:
                var_name = env_var.split("=")[0]
                var_value = env_var.split("=")[1]
                my_env[var_name] = var_value
            return my_env
        return None
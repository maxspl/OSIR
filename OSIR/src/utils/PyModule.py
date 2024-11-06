import os
from pathlib import Path, PureWindowsPath
import shutil
import re
import hashlib
from src.utils.AgentConfig import AgentConfig
from src.utils.BaseModule import BaseModule

from ..log.logger_config import AppLogger

logger = AppLogger(__name__).get_logger()


class PyModule():
    """
    Manages the execution of modules within a Python environment, handling both local and remote executions based on configuration.
    """
    def __init__(self, case_path: str, module_instance: BaseModule) -> None:
        """
        Initializes the PyModule instance by setting up paths, configurations, and determining execution context based on module details.

        Args:
            case_path (str): The base path for the case where module execution data is stored.
            module_instance (BaseModule): The module instance to execute.
        """
        self.case_path = case_path
        self.module = module_instance
        self.agent_config = AgentConfig()
        self.master_ip = self.agent_config.master_host
        self.drive_letter = self.agent_config.windows_mnt_point
        # self.whoami = self.whoami()

        # #  Windows box deployed locally uses 10.0.2.2 for smb communication
        # if self.master_ip in ["localhost", "127.0.0.1", "host.docker.internal", "192.168.1.77"]:  # TO REMOVE : local IP for testing purpose
        #     self.smb_host = "10.0.2.2"
        # else:
        #     self.smb_host = self.master_ip
        if self.agent_config.standalone and self.agent_config.windows_location != "remote" and self.agent_config.windows_location != "dockur":  # master and agent can be on same host but not windows box
            self.smb_host = "10.0.2.2"  # Fixed Vagrant IP for windows -> master smb communication
        else:
            self.smb_host = self.master_ip

        if self.is_wsl():
            self.smb_host = AgentConfig().wsl_host # Why not using self.agent_config ?
            
        # Default output dir is module dir
        self.default_output_dir = os.path.join(self.case_path, self.module.get_module_name())
        if not os.path.exists(self.default_output_dir):
            os.makedirs(self.default_output_dir)
            os.chmod(self.default_output_dir, 0o777)  # Set directory permissions to 777

    def run_ext_tool(self) -> bool:
        """
        Executes an external tool based on the module's configuration and the operating system.

        Returns:
            bool: True if the tool executes successfully, False otherwise.
        """

        logger.debug(f"Run external tool by PyModule : {self.module.module_name}")
        match self.module.processor_os:
            case 'unix':
                self.update_command_local()
                self.module.tool.run_local()
            case 'windows':
                if self.is_wsl(): # Change to adapt to remote master 
                    
                    self.update_command_wsl()
                    self.module.tool.run_wsl()
                else:
                    self.update_command_remote()
                    self.module.tool.run_remote()
        if self.module.output.type == "multiple_files" and self.module.output.output_prefix:
            self._rename_items_recursively()

    def is_wsl(self) -> bool:
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

    def update_command_remote(self):
        """
        Modifies the command string for remote execution, incorporating environmental variables and configuration specifics.
        """
        # Replace {drive} in tool path and in cmd
        if self.module.tool.path:
            self.module.tool.path = self.module.tool.path.replace(
                "{drive}", self.drive_letter + ":"
            )
            self.module.tool.cmd = self.module.tool.cmd.replace(
                "{drive}", self.drive_letter + ":"
            )

        # Replace input dir
        if self.module.input.dir:
            sanitized_input_dir = self.module.input.dir.replace("$","`$")
            self.module.tool.cmd = self.module.tool.cmd.replace(
                "{input_dir}", self._windows_suffix(sanitized_input_dir)
            )

        # Replace input file
        if self.module.input.file:
            sanitized_input_file = self.module.input.file.replace("$","`$")
            self.module.tool.cmd = self.module.tool.cmd.replace(
                "{input_file}", self._windows_suffix(sanitized_input_file)
            )

        # Format and Replace output file
        if self.module.output.output_file != '':
            self._format_output_file()
            # If output dir specified in cmd, only output file base name is used, not full path
            if "output_dir" in self.module.tool.cmd:
                self.module.tool.cmd = self.module.tool.cmd.replace(
                    "{output_file}", self.module.output.output_file
                )
            else:
                self.module.tool.cmd = self.module.tool.cmd.replace(
                    "{output_file}", self._windows_suffix(os.path.join(self.default_output_dir, self.module.output.output_file))
                )

        # Format and Replace output dir
        if self.module.output.output_dir != '':
            self._format_output_dir()
            self.module.tool.cmd = self.module.tool.cmd.replace(
                "{output_dir}", self._windows_suffix(os.path.join(self.default_output_dir, self.module.output.output_dir))
            )

        else:  # if output_dir not specified in config file, can still use module dir as output_dir
            if "output_dir" in self.module.tool.cmd:
                self.module.output.output_dir = self.default_output_dir  # necessary for prefix renaming
                self.module.tool.cmd = self.module.tool.cmd.replace("{output_dir}", self._windows_suffix(self.module.output.output_dir))

        # Format and Replace output prefix
        if self.module.output.output_prefix != '':
            self._format_output_prefix()
            self.module.tool.cmd = self.module.tool.cmd.replace(
                "{output_dir}", os.path.join(self.default_output_dir, self.module.output.output_prefix)
            )

        # Replace optional config key in cmd
        if "{optional_" in self.module.tool.cmd:
            if self.module.optional:
                for key, value in self.module.optional.items():
                    placeholder = f"{{optional_{key}}}"
                    self.module.tool.cmd = self.module.tool.cmd.replace(placeholder, value)
            else:
                logger.warning(f"optional args seems required in cmd {self.module.tool.cmd} but does not seem to be specified in configuration")

        # Replace case_name in cmd
        self.module.tool.cmd = self.module.tool.cmd.replace("{case_name}", os.path.basename(self.case_path).lower())  # lower is needed for Splunk (indexes are always lower case)

        # Replace master host in cmd for SMB communication
        self.module.tool.cmd = self.module.tool.cmd.replace(
            "{master_host}", self.smb_host
        )

    def update_command_wsl(self):
        """
        Adjusts command strings for execution within Windows Subsystem for Linux, considering path conversions and environment specifics.
        """
        
        # Replace {drive} in tool path and in cmd
        if self.module.tool.path:
            self.module.tool.path = self.module.tool.path.replace(
                "{drive}", self.drive_letter + ":"
            )
            self.module.tool.cmd = self.module.tool.cmd.replace(
                "{drive}", self.drive_letter + ":"
            )

        # Replace input dir
        if self.module.input.dir:
            self.module.tool.cmd = self.module.tool.cmd.replace(
                "{input_dir}", self._wsl_suffix(self.module.input.dir)
            )

        # Replace input file
        if self.module.input.file:
            self.module.tool.cmd = self.module.tool.cmd.replace(
                "{input_file}", self._wsl_suffix(self.module.input.file)
            )
        
        # Format and Replace output file
        if self.module.output.output_file != '':
            self._format_output_file()
            # If output dir specified in cmd, only output file base name is used, not full path
            if "output_dir" in self.module.tool.cmd:
                self.module.tool.cmd = self.module.tool.cmd.replace(
                    "{output_file}", self.module.output.output_file
                )
            else:
                self.module.tool.cmd = self.module.tool.cmd.replace(
                    "{output_file}", self._wsl_suffix(os.path.join(self.default_output_dir, self.module.output.output_file))
                )

        # Format and Replace output dir
        if self.module.output.output_dir != '':
            self._format_output_dir()
            self.module.tool.cmd = self.module.tool.cmd.replace(
                "{output_dir}", self._wsl_suffix(os.path.join(self.default_output_dir, self.module.output.output_dir))
            )

        else:  # if output_dir not specified in config file, can still use module dir as output_dir
            if "output_dir" in self.module.tool.cmd:
                self.module.output.output_dir = self.default_output_dir  # necessary for prefix renaming
                self.module.tool.cmd = self.module.tool.cmd.replace("{output_dir}", self._wsl_suffix(self.module.output.output_dir))
        
        # Format and Replace output prefix
        if self.module.output.output_prefix != '':
            self._format_output_prefix()
            self.module.tool.cmd = self.module.tool.cmd.replace(
                "{output_dir}", os.path.join(self.default_output_dir, self.module.output.output_prefix)
            )

        # Replace optional config key in cmd
        if "{optional_" in self.module.tool.cmd:
            if self.module.optional:
                for key, value in self.module.optional.items():
                    placeholder = f"{{optional_{key}}}"
                    self.module.tool.cmd = self.module.tool.cmd.replace(placeholder, value)
            else:
                logger.warning(f"optional args seems required in cmd {self.module.tool.cmd} but does not seem to be specified in configuration")

        # Replace case_name in cmd
        self.module.tool.cmd = self.module.tool.cmd.replace("{case_name}", os.path.basename(self.case_path).lower())  # lower is needed for Splunk (indexes are always lower case)
        
        # Replace master host in cmd for SMB communication
        self.module.tool.cmd = self.module.tool.cmd.replace(
            "{master_host}", self.smb_host
        )

    def update_command_local(self):
        """
        Modifies the command string for local execution based on the module's input and output configurations.
        """

        # Replace input dir
        if self.module.input.dir:
            self.module.tool.cmd = self.module.tool.cmd.replace(
                "{input_dir}", self.module.input.dir
            )

        # Replace input file
        if self.module.input.file:
            self.module.tool.cmd = self.module.tool.cmd.replace(
                "{input_file}", self.module.input.file
            )

        # Format and Replace output file
        if self.module.output.output_file != '':
            self._format_output_file()
            # If output dir specified in cmd, only output file base name is used, not full path
            if "output_dir" in self.module.tool.cmd:
                self.module.tool.cmd = self.module.tool.cmd.replace(
                    "{output_file}", self.module.output.output_file
                )
            else:
                self.module.tool.cmd = self.module.tool.cmd.replace(
                    "{output_file}", os.path.join(self.default_output_dir, self.module.output.output_file)
                )

        # Format and Replace output dir
        if self.module.output.output_dir != '':
            self._format_output_dir()
            self.module.tool.cmd = self.module.tool.cmd.replace(
                "{output_dir}", os.path.join(self.default_output_dir, self.module.output.output_dir)
            )
        else:  # if output_dir not specified in config file, can still use module dir as output_dir
            # if "output_dir" in self.module.tool.cmd:
            self.module.output.output_dir = self.default_output_dir  # necessary for prefix renaming
            self.module.tool.cmd = self.module.tool.cmd.replace("{output_dir}", self.module.output.output_dir)

        # Format and Replace output prefix
        if self.module.output.output_prefix != '':
            self._format_output_prefix()
            self.module.tool.cmd = self.module.tool.cmd.replace(
                "{output_dir}", os.path.join(self.default_output_dir, self.module.output.output_prefix)
            )

        # Replace optional config key in cmd
        if "{optional_" in self.module.tool.cmd:
            if self.module.optional:
                for key, value in self.module.optional.items():
                    placeholder = f"{{optional_{key}}}"
                    self.module.tool.cmd = self.module.tool.cmd.replace(placeholder, value)
            else:
                logger.warning(f"optional args seems required in cmd {self.module.tool.cmd} but does not seem to be specified in configuration")

        # Replace case_name in cmd
        self.module.tool.cmd = self.module.tool.cmd.replace("{case_name}", os.path.basename(self.case_path).lower())  # lower is needed for Splunk (indexes are always lower case)

    def _rename_items_recursively(self):
        """
        Recursively renames files and directories in the output directory with a specified prefix to organize output data.
        """
        prefix = os.path.basename(self.module.output.output_prefix)
        
        # First, we need to process all directories from the bottom of the directory tree
        prefix_extented = re.compile("^" + self.module.output.output_prefix_no_endpoint.replace("{endpoint_name}", ".*")) # Replace the endpoint name in the prefix with regex to avoid renaming files of other endpoints
        for root, dirs, files in os.walk(self.module.output.output_dir, topdown=True):
            # Rename all files in the current directory
            for file in files:
                if not prefix_extented.match(file):  # Check if the file is not already renamed
                    original_file_path = os.path.join(root, file)
                    new_file_name = prefix + file
                    new_file_path = os.path.join(root, new_file_name)
                    os.rename(original_file_path, new_file_path)
            # Rename directories only if they are not already renamed
            # We check and rename directories after processing the files to avoid path errors
            for i, dir in enumerate(dirs):
                if not prefix_extented.match(dir):
                    original_dir_path = os.path.join(root, dir)
                    new_dir_name = prefix + dir
                    new_dir_path = os.path.join(root, new_dir_name)
                    shutil.move(original_dir_path, new_dir_path)
                    dirs[i] = new_dir_name  # Update the directory list with the new name to correctly handle nested directories

    @staticmethod
    def remove_prefix(input_string: str):
        """
        Removes a specific prefix from a given string, used to handle specific path manipulations.

        Args:
            input_string (str): The string from which to remove the prefix.

        Returns:
            str: The modified string after removing the prefix.
        """
        # STATIC PATH
        parts = input_string.split('/OSIR/share', 1)
        return '/OSIR/share' + parts[1] if len(parts) > 1 else input_string

    @staticmethod
    def _wsl_suffix(in_path: str):
        """
        Converts a Unix-like path to a Windows UNC path, for wsl -> powershell operation.

        Args:
            in_path (str): The Unix-like path to convert.

        Returns:
            str: The converted Windows UNC path.
        """
        if in_path:
            # The keyword to search for in the path
            search_keyword = '/share'
            # Find the position of '/share' in the string
            position = in_path.find(search_keyword)
            # Check if '/share' is found
            if position != -1:
                # Add the length of '/share' to include it in the result
                path_to_replace = in_path[:position]
                UNC_input_path = in_path.replace(path_to_replace, "{master_host}")
                converted_UNC_input_path = str(PureWindowsPath(Path(UNC_input_path)))  # Convert path to windows
                return converted_UNC_input_path
            else:
                logger.error("Error: '/share' not found in the path")
                return "Error"
        else:
            return None

    @staticmethod
    def _windows_suffix(in_path: str):
        """
        Converts a Unix-like path to a Windows UNC path, essential for cross-environment operations.

        Args:
            in_path (str): The Unix-like path to convert.

        Returns:
            str: The converted Windows UNC path.
        """
        if in_path:  # None in some cases (output file for example)

            # The keyword to search for in the path
            search_keyword = '/share'
            # Find the position of '/share' in the string
            position = in_path.find(search_keyword)
            # Check if '/share' is found
            if position != -1:
                # Add the length of '/share' to include it in the result
                path_to_replace = in_path[:position]
                UNC_input_path = in_path.replace(path_to_replace, "\\\\{master_host}\\")
                converted_UNC_input_path = str(PureWindowsPath(Path(UNC_input_path)))  # Convert path to windows
                return converted_UNC_input_path
            else:
                logger.error("Error: '/share' not found in the path")
                return "Error"
        else:
            return None

    @staticmethod
    def _windows_suffix_docker(in_path: str):
        """
        Converts a Unix-like path to a Windows path with a 'C:' drive prefix.

        Args:
            in_path (str): The Unix-like path to convert.

        Returns:
            str: The converted Windows path with 'C:' drive prefix.
        """
        if not in_path:
            return None
        
        windows_path = PureWindowsPath(Path(in_path))
        return f"C:{windows_path}"
    
    def _format_output_file(self):
        """
        Formats the output file name based on the module's configuration, applying necessary transformations for endpoint and file names.
        """
        # {endpoint_name}--{module}-{input_file}.jsonl

        # Extract endpoint
        if self.module.input.file:
            endpoint_match = re.search(self.module.endpoint, self.module.input.file) if self.module.endpoint else False
            endpoint_name = endpoint_match.group(1) if endpoint_match else ''

        elif self.module.input.dir:
            endpoint_match = re.search(self.module.endpoint, self.module.input.dir) if self.module.endpoint else False
            endpoint_name = endpoint_match.group(1) if endpoint_match else ''

        if self.module.input.file:
            input_file_name = os.path.basename(self.module.input.file)
            max_filename_length = 255  # Maximum filename length on Linux
            if len(input_file_name) > max_filename_length:
                input_file_name = input_file_name[:max_filename_length]
                logger.debug(f"{self.module.get_module_name()} - {input_file_name} too long and has be truncated")
        else:
            input_file_name = ''

        # Replace placeholders in output_file
        self.module.output.output_file = self.module.output.output_file.format(
            endpoint_name=endpoint_name,
            module=self.module.module_name,
            input_file=input_file_name,
            input_path_hash=self._hash_path(self.module.input.file) if self.module.input.file else self._hash_path(self.module.input.dir)
        )

    def _format_output_dir(self):
        """
        Formats the output directory path based on the module's configuration, applying endpoint and file name-based transformations.
        """
        # {endpoint_name}--{module}-{input_file}

        # Get and possibly truncate input file name and dir name
        # Extract endpoint
        endpoint_match = re.search(self.module.endpoint, self.module.input.dir) if self.module.endpoint else False
        endpoint_name = endpoint_match.group(1) if endpoint_match else ''

        if self.module.input.file:
            input_file_name = os.path.basename(self.module.input.file)
            max_filename_length = 255  # Maximum filename length on Linux
            if len(input_file_name) > max_filename_length:
                input_file_name = input_file_name[:max_filename_length]
                logger.debug(f"{self.module.get_module_name()} - {input_file_name} too long and has be truncated")
        else:
            input_file_name = ''

        # Replace placeholders in output_dir
        self.module.output.output_dir = self.module.output.output_dir.format(
            endpoint_name=endpoint_name,
            module=self.module.module_name,
            input_file=input_file_name,
            input_path_hash=self._hash_path(self.module.input.file) if self.module.input.file else self._hash_path(self.module.input.dir)
        )

    def _format_output_prefix(self):
        """
        Formats the output prefix for files based on the module's configuration, particularly useful in managing multiple outputs systematically.
        """
        if self.module.input.file:
            endpoint_match = re.search(self.module.endpoint, self.module.input.file) if self.module.endpoint else False
            endpoint_name = endpoint_match.group(1) if endpoint_match else ''

        elif self.module.input.dir:
            endpoint_match = re.search(self.module.endpoint, self.module.input.dir) if self.module.endpoint else False
            endpoint_name = endpoint_match.group(1) if endpoint_match else ''

        if self.module.input.file:
            input_file_name = os.path.basename(self.module.input.file)
            max_filename_length = 255  # Maximum filename length on Linux
            if len(input_file_name) > max_filename_length:
                input_file_name = input_file_name[:max_filename_length]
                logger.debug(f"{self.module.get_module_name()} - {input_file_name} too long and has be truncated")
        else:
            input_file_name = ''

        # Replace placeholders in output_prefix
        hash = self._hash_path(self.module.input.dir)
        self.module.output.output_prefix_saved = self.module.output.output_prefix
        self.module.output.output_prefix = self.module.output.output_prefix.format(
            endpoint_name=endpoint_name,
            module=self.module.module_name,
            input_file=input_file_name,
            input_path_hash=hash
        )

        # Replace placeholders in output_prefix except endpoint name (used in _rename_items_recursively)
        self.module.output.output_prefix_no_endpoint = self.module.output.output_prefix_saved.format(
            endpoint_name="{endpoint_name}",
            module=self.module.module_name,
            input_file=input_file_name,
            input_path_hash=hash
        )


    def _hash_path(self, in_path):
        """
        Produces md5 truncated hash of a given path.

        Args:
            in_path (str): The Unix-like path of input directory or file.

        Returns:
            str: The generated hash.
        """

        # Encode the string to bytes
        encoded_string = in_path.encode()

        # Create a new MD5 hash object
        md5_hash = hashlib.md5()

        # Update the hash object with the bytes
        md5_hash.update(encoded_string)

        # Return the hexadecimal digest of the hash
        return md5_hash.hexdigest()

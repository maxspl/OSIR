import os
import yaml
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.core.OsirSingleton import singleton
from osir_lib.core.FileManager import FileManager

from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()


class BoxDetails(BaseModel):
    """
        Defines the connection parameters for a remote Windows forensic environment.

        This model stores the credentials and host information required for the agent
        to mount and interact with a remote Windows machine where forensic tools
        might be executed.

        Args:
            host (str): IP address or hostname of the remote Windows box.
            user (str): Username for authentication.
            password (str): Password for authentication.
            custom_mountpoint (str): The drive letter or path (default 'C') to be used during tasks.
    """
    host: str
    user: str
    password: str
    custom_mountpoint: str = Field(default='C')


class WindowsBoxConfig(BaseModel):
    """
        Defines the execution environment for Windows-based forensic modules.

        In the OSIR workflow, 'location' determines if the tools run locally, in a 
        Docker container (dockur), or on a remote machine. This model also allows 
        for resource allocation by specifying CPU cores, ensuring that heavy forensic 
        parsing doesn't overwhelm the host system.

        Args:
            location (str): The deployment type (e.g., 'local', 'remote', 'dockur').
            cores (int, optional): The number of CPU cores allocated to the forensic tasks.
            remote_box (BoxDetails): Nested connection details for remote execution.
    """
    location: str
    cores: Optional[int] = None  # Ajout de cores, rendu optionnel
    remote_box: BoxDetails


class MasterConfig(BaseModel):
    """
        Specifies the network coordinates of the OSIR Master node.y

        Args:
            host (str): The IP address or DNS name of the OSIR Master.
    """
    host: str


class SplunkConfig(BaseModel):
    """
        Contains the authentication and connection parameters for Splunk integration.

        Args:
            host (str): The address of the Splunk server.
            user (str): Username for the Splunk.
            password (str): Password for the Splunk.
            port (int): The destination port for data ingestion (usually HEC or forwarder).
            mport (int): The Splunk Management Port (default 8089).
            ssl (bool): Whether to use encrypted HTTPS for the connection.
    """
    host: str
    user: str
    password: str
    port: int
    mport: int
    ssl: bool  # booléen pour True/False


class FullAgentConfig(BaseModel):
    """
        The root validation model for the 'agent.yml' configuration file.

        It acts as a single point of truth, validating that the Master, Windows Box,
        and Splunk sections are correctly formatted and present before the agent starts.
    """
    master: MasterConfig
    windows_box: WindowsBoxConfig
    splunk: SplunkConfig


@singleton
class OsirAgentConfig:
    config_data: FullAgentConfig
    host_hostname: str
    host_ip_list: List[str]
    wsl_host: str
    standalone: bool
    is_wsl_mode: bool

    def __init__(self):
        """
            Initializes the Agent configuration by loading YAML data and environment variables.
        """
        self._load_config()
        self.host_hostname = os.getenv('HOST_HOSTNAME', '')
        self.host_ip_list = os.getenv('HOST_IP_LIST', '').split(",") if os.getenv('HOST_IP_LIST') else []
        self.wsl_host = os.getenv('OSIR_PATH', '')
        self.is_wsl_mode = self._is_wsl()
        self.standalone = self._is_standalone()

    def _load_config(self):
        """
            Reads and validates the 'agent.yml' file using the FullAgentConfig model.

            Raises:
                FileNotFoundError: If the config file is missing.
                YAMLError: If the file format is invalid.
                Exception: If validation fails against the Pydantic models.
        """
        try:
            with open(FileManager.get_config_path('agent'), 'r') as file:
                data = yaml.safe_load(file)

            self.config_data = FullAgentConfig.model_validate(data)
        except FileNotFoundError as e:
            logger.warning(f"Missing agent.yml: {e}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            raise
        except Exception as e:
            logger.error("Failed to load or validate agent configuration. " + str(e))
            raise

    @property
    def smb_host(self):
        """
            Resolves the correct IP address or hostname for SMB communication.

            Returns:
                str: The resolved hostname or IP for file sharing services.
        """
        if self.standalone and self.windows_location != "remote" and self.windows_location != "dockur":
            return "10.0.2.2"
        else:
            return self.master_host

        if self.is_wsl():
            return self.wsl_host

    @property
    def master_host(self) -> str:
        return self.config_data.master.host

    @property
    def windows_location(self) -> str:
        return self.config_data.windows_box.location

    @property
    def windows_user(self) -> str:
        return self.config_data.windows_box.remote_box.user

    @property
    def windows_password(self) -> str:
        return self.config_data.windows_box.remote_box.password

    @property
    def windows_mnt_point(self) -> str:
        return self.config_data.windows_box.remote_box.custom_mountpoint

    @property
    def windows_host(self) -> str:
        return self.config_data.windows_box.remote_box.host

    @property
    def splunk_host(self) -> str:
        return self.config_data.splunk.host

    @property
    def splunk_user(self) -> str:
        return self.config_data.splunk.user

    @property
    def splunk_password(self) -> str:
        return self.config_data.splunk.password

    @property
    def splunk_port(self) -> int:
        return self.config_data.splunk.port

    @property
    def splunk_mport(self) -> int:
        return self.config_data.splunk.mport

    @property
    def splunk_ssl(self) -> bool:
        return self.config_data.splunk.ssl

    def _is_standalone(self) -> bool:
        """
            Determines if the Agent is running on the same physical or virtual host as the Master.

            Returns:
                bool: True if the Agent and Master share the same host, False otherwise.
        """
        master_host = self.master_host

        if master_host in ["127.0.0.1", "localhost", "host.docker.internal"]:
            return True
        elif master_host == self.host_hostname:
            return True
        else:
            for host_ip in self.host_ip_list:
                if host_ip == master_host:
                    return True
        return False

    def _is_wsl(self) -> bool:
        """
            Detects if the Agent is executing within a Windows Subsystem for Linux environment.

            Returns:
                bool: True if the kernel signature matches Microsoft/WSL, False otherwise.
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

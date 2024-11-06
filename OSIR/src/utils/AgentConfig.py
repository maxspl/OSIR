import os
import yaml
from src.log.logger_config import AppLogger
from src.utils.singleton import singleton

logger = AppLogger(__name__).get_logger()


@singleton
class AgentConfig:
    """
    A singleton class that parses configuration settings from a YAML file for an agent setup.
    The configuration includes network and authentication details for master and Windows remote boxes.
    """
    # master:
    #     host: 10.10.10.1
    # windows_box:
    #     location: remote
    #     remote_box:
    #         host: 10.10.10.2
    #         user: vagrant
    #         password: vagrant
    #         custom_mountpoint: C

    def __init__(self):
        """
        Initializes the AgentConfig object by reading the YAML configuration file, parsing its contents,
        and setting up relevant instance variables for master and Windows remote box settings.
        """
        # Open agent config
        directory = os.path.dirname(__file__)  # Gets the directory of the current script
        relative_path = os.path.join(directory, '..', '..', '..', 'setup', 'conf', 'agent.yml')
        absolute_path = os.path.abspath(relative_path)  # Converts to absolute path
        self.agent_config = absolute_path
        self._parse()
        self.master_host = self.get_master_details()['host']
        self.windows_location = self.data.get('windows_box', '{}')['location']
        self.windows_user = self.data.get('windows_box', '{}')['remote_box']['user']
        self.windows_password = self.data.get('windows_box', '{}')['remote_box']['password']
        self.windows_mnt_point = self.data.get('windows_box', {}).get('remote_box', {}).get('custom_mountpoint') or 'C'
        self.windows_host = self.data.get('windows_box', '{}')['remote_box']['host']
        self.splunk_host = self.get_splunk_details()['host']

        self.host_hostname = os.getenv('HOST_HOSTNAME', '')
        self.host_ip_list = os.getenv('HOST_IP_LIST', '').split(",") if os.getenv('HOST_IP_LIST') else []
        # TODO Go throw fifos to retrieve the windows path to OSIR
        if self.is_wsl():
            # self.wsl_host = "\\\\wsl.localhost\\Ubuntu-22.04\\opt\\OSIR_wsl\\OSIR"
            self.wsl_host = os.getenv('OSIR_PATH', '')
        self.standalone = self.standalone()

    def _parse(self):
        """
        Parses the YAML file to retrieve agent configuration.
        Handles errors by logging them.

        Args:
            None

        Returns:
            None: Modifies the instance variable `self.data` with the parsed data.
        """
        with open(self.agent_config, 'r') as file:
            try:
                self.data = yaml.safe_load(file)
            except Exception as e:
                logger.error("Failed to load module. Error: " + str(e))

    def get_windows_box_details(self):
        """
        Retrieves the configuration details specific to the Windows remote box.

        Args:
            None

        Returns:
            dict: A dictionary containing the configuration details of the Windows remote box.
        """
        return self.data.get('windows_box', '{}')

    def get_master_details(self):
        """
        Retrieves the configuration details specific to the master.

        Args:
            None

        Returns:
            dict: A dictionary containing the configuration details of the master.
        """
        return self.data.get('master', '{}')

    def standalone(self):
        """
        Determines if the agent is in standalone mode based on the master location.
        Standalone mode is enabled if the master is running locally.

        Args:
            None

        Returns:
            bool: True if the agent is running in standalone mode, False otherwise.
        """

        # Check if master IP is local host
        if self.master_host in ["127.0.0.1", "localhost", "host.docker.internal"]:
            return True
        # Check if master host if host hostname
        elif self.master_host == self.host_hostname:
            return True
        else:
            # Check if master IP is one of the host IP
            for host_ip in self.host_ip_list:
                if host_ip == self.master_host:
                    return True
        return False

    def get_splunk_details(self):
        """
        Retrieves the configuration details specific to the master.

        Args:
            None

        Returns:
            dict: A dictionary containing the configuration details of the master.
        """
        return self.data.get('splunk', '{}')

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

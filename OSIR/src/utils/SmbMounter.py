from src.utils.AgentConfig import AgentConfig
# from src.log.logger import AppLogger
from src.log.logger_config import AppLogger

import subprocess
import os
import time
import threading

logger = AppLogger().get_logger()


class SMBMounter:
    """
    Manages the mounting, monitoring, and unmounting of an SMB share, ensuring continuous accessibility.
    """
    def __init__(self, mount_point, username=None, password=None, version='3.0', check_interval=15):
        """
        Initializes the SMBMounter with the necessary parameters for mounting an SMB share.

        Args:
            mount_point (str): The local directory where the SMB share will be mounted.
            username (Optional[str]): The username for accessing the SMB share.
            password (Optional[str]): The password for accessing the SMB share.
            version (str): The SMB protocol version to use.
            check_interval (int): The interval in seconds between checks to ensure the mount is still active.
        """
        self.mount_point = mount_point
        self.username = username
        self.password = password
        self.version = version
        self.check_interval = check_interval
        self.test_file = os.path.join(mount_point, )
        self._stop_event = threading.Event()
        
        # Mount SMB share if remote master
        self.agent_config = AgentConfig()
        if self.agent_config.standalone:
            logger.debug('Standalone mode. Files accessed on disk')
            self.standalone = True
        else:
            logger.info('Agent is not on the same host as master. Files accessed via SMB mounting')
            self.standalone = False
            self.master_host = self.agent_config.get_master_details()['host']
            self.share = f"//{self.master_host}/share"
            self.test_file = os.path.join(mount_point, "smb_test_file")  # File created by master_setup.sh
            
    def _is_mounted(self):
        """
        Checks if the SMB share is currently mounted.

        Returns:
            bool: True if the share is mounted, False otherwise.
        """
        with open("/proc/mounts", "r") as f:
            mounts = f.read()
            if self.mount_point.rstrip('/') not in mounts:
                return False
            else:
                return True

    def _can_access_file(self):
        """
        Verifies whether a test file or directory within the mounted SMB share is accessible.

        Returns:
            bool: True if the test file is accessible, False if it is not or if the mount point is inaccessible.
        """
        # Attempt to access a test file or directory within the mount point
        try:
            if os.path.isdir(self.test_file):
                os.listdir(self.test_file)  # List directory contents to check accessibility
            else:
                with open(self.test_file, 'r') as f:
                    f.read(1)  # Read the first byte to check file accessibility
            return True
        except Exception as e:
            logger.warning(f"Mount point {self.mount_point} is listed /proc/mount but {self.test_file} not accessible. Error: {e}")
            logger.debug("Unmounting before mount retry ...")
            self.unmount()
            return False

    def mount(self):
        """
        Attempts to mount the SMB share at the specified mount point.

        Returns:
            bool: True if the share is successfully mounted, False otherwise.
        """
        if self._is_mounted():
            logger.debug(f"{self.mount_point} is already mounted.")
            return True
        # Ensure the mount point exists
        if not os.path.isdir(self.mount_point):
            os.makedirs(self.mount_point)

        # Build the mount command
        command = [
            'mount', '-t', 'cifs',
            self.share, self.mount_point,
            '-o', f'username={self.username},password={self.password},vers={self.version}'
        ]
        
        # Execute the mount command
        try:
            subprocess.run(command, check=True)
            logger.info(f"Mounted {self.share} at {self.mount_point}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to mount {self.share}: {e}")
            return False

    def unmount(self):
        """
        Attempts to unmount the SMB share.

        Returns:
            bool: True if the share is successfully unmounted, False otherwise.
        """
        if not self._is_mounted():
            logger.debug(f"{self.mount_point} is not mounted.")
            return True
        
        command = ['umount', self.mount_point]
        try:
            subprocess.run(command, check=True)
            logger.info(f"Unmounted {self.mount_point}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to unmount {self.mount_point}: {e}")
            return False

    def _check_and_remount(self):
        """
        Periodically checks if the SMB share is mounted and accessible, and attempts to remount it if not.
        This function is intended to be run in a separate thread.
        """
        while not self._stop_event.is_set():
            if not self._is_mounted() or not self._can_access_file():
                logger.warning(f"{self.mount_point} is not mounted or not accessible. Attempting to remount.")
                self.mount()
            else:
                logger.debug(f"{self.mount_point} is mounted and accessible.")
            time.sleep(self.check_interval)

    def start_monitoring(self):
        """
        Starts a background thread that continuously monitors the mount point to ensure it remains mounted and accessible.
        """
        # self._check_and_remount()
        self._monitor_thread = threading.Thread(target=self._check_and_remount)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        logger.info("Started monitoring the mount point")

        # Block until the thread terminates
        # self._monitor_thread.join()

    def stop_monitoring(self):
        """
        Stops the monitoring thread.
        """
        self._stop_event.set()
        self._monitor_thread.join()
        logger.info("Stopped monitoring the mount point.")

# Example usage:
# mounter = SMBMounter("//192.168.1.77/share", "/OSIR/share/", "guest", "", check_interval=60, test_file="/OSIR/share/some_test_file_or_dir")
# mounter.mount()
# mounter.start_monitoring()
# mounter.stop_monitoring()
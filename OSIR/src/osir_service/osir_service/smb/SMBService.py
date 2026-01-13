import subprocess
import os
import time
import threading

from osir_lib.logger import AppLogger
from osir_lib.core.OsirAgentConfig import OsirAgentConfig

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
        self.agent_config = OsirAgentConfig()
        if self.agent_config.standalone:
            logger.debug('Standalone mode. Files accessed on disk')
            self.standalone = True
        else:
            logger.info('Agent is not on the same host as master. Files accessed via SMB mounting')
            self.standalone = False
            self.master_host = self.agent_config.master_host
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

    def upload_file(self, local_path: str, remote_relative_path: str) -> bool:
        """
        Copies a file from the local filesystem to the mounted SMB share (Upload).

        Args:
            local_path (str): The absolute or relative path of the file to upload locally.
            remote_relative_path (str): The path relative to the mount point where the file should be placed.
                                        Ex: 'results/report.json'
        
        Returns:
            bool: True if the file was uploaded successfully, False otherwise.
        """
        if self.standalone:
            logger.error("Cannot upload: Agent is in standalone mode (files are already local).")
            return False

        if not self._is_mounted():
            logger.error("Cannot upload: SMB share is not mounted.")
            return False

        if not os.path.exists(local_path):
            logger.error(f"Cannot upload: Local file not found at {local_path}.")
            return False

        # Le chemin de destination est le point de montage + le chemin relatif distant
        remote_full_path = os.path.join(self.mount_point, remote_relative_path)
        
        # Assurez-vous que le répertoire distant existe avant de copier
        remote_dir = os.path.dirname(remote_full_path)
        if not os.path.isdir(remote_dir):
            try:
                os.makedirs(remote_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create remote directory {remote_dir} on SMB share: {e}")
                return False

        # Utilisation de la commande 'cp'
        command = ['cp', local_path, remote_full_path]
        
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info(f"Successfully uploaded {local_path} to {remote_full_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Upload failed (cp command error): {e.stderr.strip()}")
            return False
        except FileNotFoundError:
            logger.error("Upload failed: 'cp' command not found (check environment PATH).")
            return False


    def download_file(self, remote_relative_path: str, local_path: str) -> bool:
        """
        Copies a file from the mounted SMB share to the local filesystem (Download).

        Args:
            remote_relative_path (str): The path relative to the mount point of the file to download.
                                        Ex: 'files/input.txt'
            local_path (str): The local destination path (can be a directory or a file path).

        Returns:
            bool: True if the file was downloaded successfully, False otherwise.
        """
        if self.standalone:
            logger.error("Cannot download: Agent is in standalone mode (files are already local).")
            return False

        if not self._is_mounted():
            logger.error("Cannot download: SMB share is not mounted.")
            return False

        # Le chemin source est le point de montage + le chemin relatif distant
        remote_full_path = os.path.join(self.mount_point, remote_relative_path)
        
        if not os.path.exists(remote_full_path):
            logger.error(f"Cannot download: Remote file not found at {remote_full_path} on the SMB share.")
            return False

        # Assurez-vous que le répertoire local de destination existe
        local_dir = os.path.dirname(local_path)
        if local_dir and not os.path.isdir(local_dir):
            try:
                os.makedirs(local_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create local destination directory {local_dir}: {e}")
                return False

        # Utilisation de la commande 'cp'
        command = ['cp', remote_full_path, local_path]
        
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info(f"Successfully downloaded {remote_full_path} to {local_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Download failed (cp command error): {e.stderr.strip()}")
            return False
        except FileNotFoundError:
            logger.error("Download failed: 'cp' command not found (check environment PATH).")
            return False
        
# Example usage:
# mounter = SMBMounter("//192.168.1.77/share", "/OSIR/share/", "guest", "", check_interval=60, test_file="/OSIR/share/some_test_file_or_dir")
# mounter.mount()
# mounter.start_monitoring()
# mounter.stop_monitoring()
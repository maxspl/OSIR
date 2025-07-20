import os
import re
import csv
from typing import List, Optional, Tuple

from src.utils.BaseModule import BaseModule
from src.utils.PyModule import PyModule
from src.log.logger_config import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


class ANSSI_Decode(PyModule):
    """
    PyModule to apply DECODE tool on NTFS_info files with Listdlls when available.
    """

    def __init__(self, case_path: str, module: BaseModule):
        """
        Initializes the Module.

        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (BaseModule): Instance of BaseModule containing configuration details for the extraction process.
        """
        super().__init__(case_path, module)

        # Input directory, should be extracted_files/General/NTFSInfoFull_detail/
        self._ntfs_info_dir: str = module.input.dir
        self._endpoint: str = module.endpoint

        # Save cmd with place‑holders for further iterations
        self._cmd: str = self.module.tool.cmd

    # =========================================================================
    # Public entry point
    # =========================================================================
    def __call__(self) -> bool:
        """
        Execute the internal processor of the module.

        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        logger.debug("Processing dir %s", self.module.input.dir)
        try:
            self._apply_decode()
        except Exception as exc:          # noqa: BLE001 (broad except is fine here)
            logger.error("Unable to run decode: %s", exc, exc_info=True)
            return False

        logger.debug("%s done", self.module.module_name)
        return True

    # =========================================================================
    # High‑level orchestration
    # =========================================================================
    def _apply_decode(self) -> None:
        """
        Discover inputs, prepare the command line for each and run the decoder.
        """
        jobs = self._find_input()
        if not jobs:
            logger.warning("No NTFSInfo CSV file found. Nothing to do.")
            return

        for ntfs_info_file, mount_point, listdlls in jobs:
            if self._prepare_input(ntfs_info_file, mount_point, listdlls):
                self._run_decode()

    # =========================================================================
    # External‑tool helpers
    # =========================================================================
    def _run_decode(self) -> None:
        """Launch the external decoding tool and restore the pristine command."""
        self.run_ext_tool()
        # Restore cmd with place‑holders because they are erased by _prepare_input
        self.module.tool.cmd = self._cmd

    # =========================================================================
    # Discovery helpers
    # =========================================================================
    def _find_input(self) -> List[Tuple[str, str, Optional[str]]]:
        """
        Scan *self._ntfs_info_dir* to discover every NTFSInfo CSV to decode.

        Returns:
            list[tuple]: Each tuple contains (ntfs_info_file, mount_point|volume_id, listdlls_path|None).
        """
        jobs: List[Tuple[str, str, Optional[str]]] = []

        for root, _dirs, files in os.walk(self._ntfs_info_dir):
            # Check if we are in the NTFSInfoFull_detail directory
            if not root.endswith("NTFSInfoFull_detail"):
                continue

            # Retrieve NTFSInfo*.csv files
            for filename in files:
                if not (filename.startswith("NTFSInfo") and filename.endswith(".csv")):
                    continue

                ntfs_info_file = os.path.join(root, filename)
                logger.debug("Found NTFSInfo CSV: %s", ntfs_info_file)

                # Check for Listdlls.txt in General directory (parent directory)
                general_dir = os.path.dirname(root)
                listdlls_path = os.path.join(general_dir, "Listdlls.txt")
                if os.path.isfile(listdlls_path):
                    logger.debug("Found Listdlls.txt: %s", listdlls_path)
                else:
                    logger.debug("Listdlls.txt not found in %s", general_dir)
                    listdlls_path = None

                # Get mount point or fallback volume ID
                mount_point = self._get_mount_point_or_volume_id(
                    ntfs_info_file,
                    root,
                )
                logger.debug("Mount Point or Volume ID: %s", mount_point)

                jobs.append((ntfs_info_file, mount_point or "unknown", listdlls_path))

        return jobs

    def _get_mount_point_or_volume_id(self, ntfs_info_file: str, ntfs_dir: str) -> Optional[str]:
        """
        Try to get the mount‑point letter from volstats.csv if it exists.
        If not possible, return the VolumeID extracted from the NTFSInfo file
        name.

        Args:
            ntfs_info_file (str): Path to the NTFSInfo CSV.
            ntfs_dir (str): Directory that should contain volstats.csv.

        Returns:
            str | None: Drive letter (C, D, …), VolumeID (0x…), or *None*.
        """
        volstats_file = os.path.join(ntfs_dir, "volstats.csv")

        # ------------------------------------------------------------------ #
        # Extract VolumeID from filename as fallback
        # Example: NTFSInfo_00000000_DiskInterface_0x8a4c79c84c79b015_.csv
        # ------------------------------------------------------------------ #
        fallback_volume_id: Optional[str] = None
        try:
            for part in os.path.basename(ntfs_info_file).split("_"):
                if part.startswith("0x"):
                    fallback_volume_id = part
                    break
        except Exception:
            logger.exception("Failed to extract VolumeID from filename.")

        # ------------------------------------------------------------------ #
        # Try reading volstats.csv
        # ------------------------------------------------------------------ #
        if os.path.isfile(volstats_file):
            logger.debug(f"volstats_file found : {volstats_file}")
            try:
                with open(volstats_file, encoding="utf-8") as f_desc:
                    reader = csv.DictReader(f_desc)
                    for row in reader:
                        if row.get("VolumeID").lower() == fallback_volume_id.lower():
                            mount_point = row.get("MountPoint", "").strip()
                            if mount_point:
                                # Remove ":\" from mount point if present (e.g. C:\ -> C)
                                return mount_point.replace(":\\", "")
            except Exception as exc:
                logger.error("Error reading volstats.csv: %s", exc)

        # If no mount point found, return fallback VolumeID
        return fallback_volume_id

    # =========================================================================
    # Input preparation helpers
    # =========================================================================
    def _prepare_input(self, ntfs_info_file: str, mount_point: str, listdlls_path: Optional[str], ) -> bool:
        """
        Replace place‑holders in *self.module.tool.cmd* with concrete values.

        Args:
            ntfs_info_file (str): NTFSInfo CSV to decode.
            mount_point (str): Drive letter or VolumeID for the current CSV.
            listdlls_path (str | None): Path to Listdlls.txt if available.
        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        endpoint_regex = self.module.endpoint
        match = re.search(endpoint_regex, ntfs_info_file)
        if match:
            endpoint_name = match.group(1)
        else:
            logger.error("Endpoint regex matched nothing")
            return False
        
        output_dir = os.path.join(self.case_path, self.module.module_name, endpoint_name)
        os.makedirs(output_dir, exist_ok=True)

        output_file_base = os.path.join(output_dir, f"decode_result_{mount_point}")

        # Update command with actual paths
        self.module.tool.cmd = self.module.tool.cmd.replace("{input_file}", ntfs_info_file)
        self.module.tool.cmd = self.module.tool.cmd.replace("{output_log}", f"{output_file_base}.log")
        self.module.tool.cmd = self.module.tool.cmd.replace("{output_csv}", f"{output_file_base}.csv")
        self.module.tool.cmd = self.module.tool.cmd.replace("{output_pdf}", f"{output_file_base}.pdf")

        # Add optional --dlls_file if found:
        if listdlls_path:
            self.module.tool.cmd += f" --dlls_file {listdlls_path}"

        return True
import re
from src.utils.decorator import pinfo
from src.utils.UnixUtils import UnixUtils
from ...utils.BaseModule import BaseModule
from src.utils.PyModule import PyModule
from src.log.logger_config import AppLogger, CustomLogger
from urllib.parse import unquote

logger: CustomLogger = AppLogger().get_logger()


class AuditModule(PyModule, UnixUtils):
    """
    PyModule to perform processing operations on Audit logs.
    """
    def __init__(self, case_path: str, module: BaseModule):
        """
        Initializes the Module.

        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (BaseModule): Instance of BaseModule containing configuration details for the extraction process.
        """
        PyModule.__init__(self, case_path, module)
        UnixUtils.__init__(self, case_path, module)

        self._file_to_process = module.input.file

    def __call__(self) -> bool:
        """
        Execute the internal processor of the module.

        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        try:
            writer_queue = self.start_writer_thread()
            logger.debug(f"Processing file {self._file_to_process}")

            for log in self.get_log():
                if log.strip():  # Ensure log is not empty
                    res_log = self.parse(log)
                    if res_log:
                        writer_queue.put(res_log)

            writer_queue.put(None)
            logger.debug(f"{self.module.module_name} done")
            return True
        except Exception as exc:
            logger.error_handler(exc)
            return False

    def parse(self, log):
        """
        Parse a single log entry.

        Args:
            log (str): The log entry to parse.

        Returns:
            dict: Parsed log data.
        """
        res_log = {
            "_time": self.parse_date_audit(log),
            "_raw": log,
            "tag": [],
        }

        pattern = r'\b(\w+)=([\S]+)'
        matches = re.findall(pattern, log)
        tmp_keyvalue = {key: value.strip("\"").strip("\'") for key, value in matches}
        res_log.update(tmp_keyvalue)

        # Process cmd and proctitle
        for key in ["cmd", "proctitle"]:
            if key in res_log:
                res_log[key] = self.convert_commandline(res_log[key])
                res_log["command_line"] = res_log[key]

        # Determine tags based on the type
        type_tags = {
            "process": ["BPRM_FCAPS", "CAPSET", "CWD", "EXECVE", "OBJ_PID", "PATH", "PROCTITLE", "SECCOMP", "SYSCALL", "USER_CMD"],
            "file_access": ["PATH"],
            "service": ["SERVICE_START", "SERVICE_STOP", "SYSTEM_BOOT", "SYSTEM_RUNLEVEL", "SYSTEM_SHUTDOWN"],
            "group_management": ["GRP_MGMT", "GRP_CHAUTHTOK", "ADD_GROUP", "DEL_GROUP"],
            "user_management": ["ADD_USER", "DEL_USER", "USER_MGMT", "USER_CHAUTHTOK"],
            "authentication": ["LOGIN", "USER_CMD", "GRP_AUTH", "CHUSER_ID", "CHGRP_ID", "USER_LOGIN", "USER_LOGOUT", "USER_ERR", "USER_ACCT", "ACCT_LOCK", "ACCT_UNLOCK", "USER_START", "USER_END", "CRED_ACQ", "CRED_REFR", "CRED_DISP"],
            "auditd_tampering": ["KERNEL", "CONFIG_CHANGE", "DAEMON_ABORT", "DAEMON_ACCEPT", "DAEMON_CLOSE", "DAEMON_CONFIG", "DAEMON_END", "DAEMON_ERR", "DAEMON_RESUME", "DAEMON_ROTATE", "DAEMON_START", "FEATURE_CHANGE"]
        }

        if "type" in res_log:
            for tag, types in type_tags.items():
                if res_log["type"] in types:
                    res_log["tag"].append(tag)

        return res_log

    def parse_date_audit(self, log):
        date_res = ""
        try:
            match = re.search(r"msg=audit\((\d+)", log)
            date_res = match.group(1) if match else 'N/A'
        except Exception as exc:
            logger.error_handler(exc)
        return date_res

    def convert_commandline(self, hex_value):
        """
        Convert a hexadecimal command line to a string.

        Args:
            hex_value (str): The hex value to convert.

        Returns:
            str: The converted command line.
        """
        hex_value = re.sub("([a-fA-F0-9]{2})", "%\\1", hex_value)
        return unquote(hex_value)

import re
from src.utils.UnixUtils import UnixUtils
from ...utils.BaseModule import BaseModule
from src.utils.PyModule import PyModule
from src.log.logger_config import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


class SyslogModule(PyModule, UnixUtils):
    """
    PyModule to perform processing operations on syslog.
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
        self._name_rex = self.module.input.name

        # PARSING OUTPUT STRUCTURE
        self.structure = {
            "_time": lambda log: self.get_date(
                log, r'([A-Za-z]+\s+(0[1-9]|[12][0-9]|3[01])\s+\d{2}:\d{2}:\d{2})', '%b %d %H:%M:%S'
            ),
            "hostname": lambda log: self.safe_search(r"^\S+\s+\S+\s+\S+\s+(\S+)", log),
            "app": lambda log: self.safe_search(r"^\w+\s+\d{1,2}\s\S+\s+\S+\s([^:\[]+)", log),
            "event_type": self.parse_event_type,
            "tags": self.parse_tags,
            "cron_name": lambda log: self.safe_search(r"(starting|finished)\s(.*)", log),
            "user": lambda log: self.safe_search(r":\s\(([^\)]*)\)", log) if "CMD" in log else None,
            "command_line": lambda log: self.safe_search(r"CMD\s\((.*)\)", log) if "CMD" in log else None,
            "job_name": lambda log: self.safe_search(r"Job\s\`([^\']+)'", log) if "Job" in log else None,
        }

        self._format_output_file()
    
    def __call__(self) -> bool:
        """
        Execute the internal processor of the module.

        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        try:
            writer_queue = self.start_writer_thread()
            logger.debug(f"Processing file {self.module.input.file}")

            for log in self.get_log():
                writer_queue.put(self.parse(log))

            writer_queue.put(None)
            logger.debug(f"{self.module.module_name} done")
        except Exception as exc:
            logger.error_handler(exc)

    def parse_event_type(self, log: str) -> str:
        if "starting" in log:
            return "starting_cron"
        elif "finished" in log:
            return "finished_cron"
        elif "CMD" in log:
            return "cron_process_creation"
        elif "Job" in log:
            return "job_started" if "started" in log else "job_terminated"
        elif "Restarting" in log:
            return "restarting_apparmor"
        elif "Reloading" in log:
            return "reloading_apparmor_profiles"
        return None

    def parse_tags(self, log: str) -> list:
        """
        Parse and generate tags based on the log content.
        
        Args:
            log (str): The log line to parse.
        
        Returns:
            list: Tags for the log entry.
        """
        tags = []
        if "cron" in log:
            tags.append("cron")
            if "starting" in log:
                tags.append("starting")
            elif "finished" in log:
                tags.append("finished")
            elif "CMD" in log:
                tags.extend(["execution", "process_creation"])
            elif "Job" in log:
                tags.append("job")
                tags.append("started" if "started" in log else "terminated")
        elif "apparmor" in log:
            tags.append("apparmor")
            if "Restarting" in log:
                tags.append("restarting")
            elif "Reloading" in log:
                tags.append("reloading")
        elif "containerd" in log or "dockerd" in log:
            tags.append("container")
        return tags

    def parse(self, log: str) -> dict:
        """
        Parse a single log line using the structure defined in the init.
        
        Args:
            log (str): The log line to parse.
        
        Returns:
            dict: Parsed log data.
        """
        parsed_log = {field: parser(log) for field, parser in self.structure.items()}
        parsed_log["_raw"] = log

        return parsed_log

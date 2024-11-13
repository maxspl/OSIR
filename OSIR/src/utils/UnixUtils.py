import datetime
import gzip
import json
import os
import queue
import re
import threading
from src.utils.decorator import timeit
from src.utils.BaseModule import BaseModule
from src.log.logger_config import AppLogger, CustomLogger
from typing import Callable

logger: CustomLogger = AppLogger().get_logger()


class UnixUtils:
    """
    
    A utility class for processing Unix-based log files, handling log writing, reading, and formatting.

    Attributes:
        case_path (str): Path to the directory where case-related files are stored.
        module (BaseModule): Instance of the module being used for processing.
        default_output_dir (str): Default directory path for storing output logs based on the module name.

    """
    def __init__(self, case_path: str, module_instance: BaseModule):
        self.default_output_dir = os.path.join(self.case_path, self.module.get_module_name())
        if not os.path.exists(self.default_output_dir):
            os.makedirs(self.default_output_dir)
        self.case_path: str = case_path
        self.module: BaseModule = module_instance

    @staticmethod
    def get_severity(line):
        """
        Extracts the severity level from a log line based on predefined keywords.

        Args:
            line (str): The log line from which to extract the severity.
        
        Returns:
            str: The extracted severity level in lowercase, or "N/A" if not found.
        """
        severity = re.search(r"debug|warning|info|notice|error|fatal|panic|statement|detail|log", line, re.IGNORECASE)
        return severity.group(0).lower() if severity else "N/A"
    
    @staticmethod
    def get_date(line, regex=None, strtime=None):
        """
        Parses a date from a log line based on a given regex or inferred format.

        Args:
            line (str): The log line to parse for date information.
            regex (Optional[str]): Regular expression pattern for date extraction.
            strtime (Optional[str]): Date format string for parsing.
        
        Returns:
            str: ISO formatted date string or "N/A" if no date found.
        """
        if not regex:
            regex = UnixUtils.date_format(line)

        date = re.search(regex, line)
        if date:
            datetime_object = datetime.datetime.strptime(date.group(0), strtime)
            return datetime_object.isoformat()
        
        return "N/A"
    
    def get_log(self):
        """
        Generates each line from a log file, handling .gz compressed files if needed.

        Yields:
            str: A single log line.
        """
        
        if self.module.input.file.endswith(".gz"):
            with gzip.open(self.module.input.file, 'rt') as input_file:
                for line in input_file:
                    yield line  
        else:
            with open(self.module.input.file, 'r') as input_file:
                for line in input_file:
                    yield line

    @staticmethod
    def date_format(log_line):
        """
        Determines the date format for a given log line by matching against known patterns.

        Args:
            log_line (str): The log line to analyze for date format.
        
        Returns:
            str: The matching date regex pattern or logs a warning if no format is found.
        """
        date_regexes = [
            r'^\d{4}-\d{2}-\d{2}',                    # YYYY-MM-DD
            r'^\d{2}/\d{2}/\d{4}',                    # DD/MM/YYYY
            r'^\d{2}/\d{2}/\d{4}',                    # MM/DD/YYYY
            r'^\d{4}/\d{2}/\d{2}',                    # YYYY/MM/DD
            r'^\d{2}-\d{2}-\d{4}',                    # DD-MM-YYYY
            r'^\d{2}-\d{2}-\d{4}',                    # MM-DD-YYYY
            r'^\d{2}\.\d{2}\.\d{4}',                  # DD.MM.YYYY
            r'^\d{4}\.\d{2}\.\d{2}',                  # YYYY.MM.DD
            r'^\d{2} [A-Za-z]+ \d{4}',                # DD Month YYYY
            r'^[A-Za-z]+ \d{2}, \d{4}',               # Month DD, YYYY
            r'^\d{8}',                                # YYYYMMDD
            r'^\d{6}',                                # YYMMDD
            r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}',  # YYYY/MM/DD HH:MM:SS
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # YYYY-MM-DDTHH:MM:SS
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}',  # YYYY-MM-DD HH:MM:SS.SSS
            r'^\d{2} [A-Za-z]+ \d{4}, \d{2}:\d{2}',   # DD Month YYYY, HH:MM
            r'^\d{4}-[A-Za-z]{3}-\d{2}',              # YYYY-MMM-DD
            r'^[A-Za-z]+ \d{2}',                      # Month DD
            r'^\d{2} [A-Za-z]+',                      # DD Month
            r'^\d{2}/\d{2}/\d{2}',                    # MM/DD/YY
            r'^\d{2}/\d{2}/\d{2}',                    # DD/MM/YY
            r'^\d{2}-\d{2}-\d{2}',                    # MM-DD-YY
            r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}',        # YYYY/MM/DD HH:MM
            r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}',        # DD/MM/YYYY HH:MM
            r'^\d{14}',                               # YYYYMMDDHHMMSS
            r'^\d{8}',                                # MMDDYYYY
            r'^\d{2} [A-Za-z]+, \d{4}',               # DD Month, YYYY
            r'^\d{4}/\d{2}/\d{2}T\d{2}:\d{2}:\d{2}Z',  # YYYY/MM/DDTHH:MM:SSZ
            r'^\d{2}-\d{2}-\d{2}',                    # YY-MM-DD
            r'^\d{2}/\d{4}',                          # MM/YYYY
            r'^\d{4}/\d{2}',                          # YYYY/MM
            r'^[A-Za-z]{3} \d{2}, \d{4}',             # MMM DD, YYYY
            r'^\d{2} [A-Za-z]{3} \d{4}',              # DD MMM YYYY
            r'^\d{2}-[A-Za-z]{3}-\d{4}',              # DD-MMM-YYYY
            r'^\d{2}\.\d{2}\.\d{2}',                  # DD.MM.YY
            r'^[A-Za-z]+ \d{2} \d{4}',                # Month DD YYYY
            r'^\d{2}-\d{2}',                          # MM-YY
            r'^[A-Za-z]+\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}',  # Mon DD HH:MM:SS -> Aug 7 10:15:50
            r'\d{10}\.\d{3}:\d{2,3}'                  # 1693982401.546:86 -> msg=audit(1693982401.546:86)
        ]
        regex_match = []
        for i, regex in enumerate(date_regexes):
            if re.match(regex, log_line):
                regex_match.append(regex)
            if re.search(regex, log_line):
                regex_match.append(regex)
        if not len(regex_match):
            logger.warning(f"No matching date format found in line : {log_line:<50.50}")
            return False
        else:
            return max(regex_match)

    @timeit
    def _thread_save_jsonl(self, queue, output_path=None):
        """
        Saves queued log data to a JSONL file in a threaded manner.

        Args:
            queue (Queue): Queue containing log data.
            output_path (Optional[str]): Path to save the output JSONL file. If None, generated based on module endpoint.
        """
        logger.debug("ici")
        if not output_path:
            pattern = re.compile(self.module.endpoint)
            match = pattern.search(self.module.input.file)
            endpoint_name = match.groups()[0]
            output_path = os.path.join(self.default_output_dir, endpoint_name)

            if not os.path.exists(output_path):
                os.makedirs(output_path, exist_ok=True)

            output_path = os.path.join(output_path, os.path.basename(self.module.input.file)+'.jsonl')
        logger.debug(output_path)
        with open(output_path, "a") as file:
            while True:
                logger.debug("ici")
                data = queue.get()
                if data is None:
                    break
                json.dump(data, file)
                file.write('\n')
                queue.task_done()

    def start_writer_thread(self):
        """
        Starts a writer thread that will handle saving data to JSONL files.

        Returns:
            Queue: A queue that will hold data to be processed by the writer thread.
        """
        q = queue.Queue()
        writer_thread = threading.Thread(target=self._thread_save_jsonl, args=(q,))
        writer_thread.start()
        return q
    
    def safe_search(self, pattern: str, log: str) -> str:
        """
        Searches for a regex pattern in a log line and returns the first group if found.

        Args:
            pattern (str): Regex pattern to search for.
            log (str): The log line to search within.
        
        Returns:
            str: First matching group, or None if no match is found.
        """
        match = re.search(pattern, log)
        return match.group(1) if match else None

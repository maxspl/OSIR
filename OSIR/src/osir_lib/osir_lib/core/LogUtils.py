import datetime
import gzip
import json
import queue
import re
import threading
import lzma
from pathlib import Path

from osir_lib.core.OsirModule import OsirModule
from osir_lib.core.OsirDecorator import timeit
from osir_lib.logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


class LogUtils:
    """

    A utility class for processing Unix-based log files, handling log writing, reading, and formatting.

    Attributes:
        case_path (str): Path to the directory where case-related files are stored.
        module (OsirModule): Instance of the module being used for processing.
        default_output_dir (str): Default directory path for storing output logs based on the module name.

    """

    def __init__(self, ctx: OsirModule):
        self.ctx: OsirModule = ctx

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

    def _source_datetime(self) -> datetime.datetime:
        """
        Best guess at when the log file being parsed was last written.

        Uses the artifact mtime. Falls back to the current time when the path is unavailable.

        Returns:
            datetime.datetime: Naive UTC datetime of the file's last write.
        """
        try:
            mtime = Path(str(self.ctx.input.match)).stat().st_mtime
            return datetime.datetime.fromtimestamp(mtime, datetime.timezone.utc).replace(tzinfo=None)
        except (AttributeError, OSError, TypeError, ValueError):
            return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

    def get_date(self, line, regex=None, strtime=None):
        """
        Parses a date from a log line based on a given regex or inferred format.

        RFC3164 syslog timestamps carry no year, so strptime defaults them to
        1900.

        Args:
            line (str): The log line to parse for date information.
            regex (Optional[str]): Regular expression pattern for date extraction.
            strtime (Optional[str]): Date format string for parsing.

        Returns:
            str: ISO formatted date string or "N/A" if no date found.
        """
        if not regex:
            regex = LogUtils.date_format(line)

        date = re.search(regex, line)
        if date:
            try:
                datetime_object = datetime.datetime.strptime(date.group(0), strtime)
            except (ValueError, TypeError):
                logger.debug(f"Unparseable date {date.group(0)!r} for format {strtime!r}")
                return "N/A"

            if datetime_object.year == 1900 and '%Y' not in (strtime or '') and '%y' not in (strtime or ''):
                source_dt = self._source_datetime()
                year = source_dt.year
                try:
                    datetime_object = datetime_object.replace(year=year)
                except ValueError:
                    datetime_object = datetime_object.replace(year=year, day=28)

                # A log rotated in January still holds December lines. No line
                # can postdate the file last write, so anything past the mtime
                # (one day of margin for clock skew) belongs to the year before.
                if datetime_object > source_dt + datetime.timedelta(days=1):
                    datetime_object = datetime_object.replace(year=year - 1)

            return datetime_object.isoformat()

        return "N/A"

    def get_log(self):
        """
        Generates each line from a log file, handling .gz and .xz compressed files if needed.

        Yields:
            str: A single log line.
        """
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'windows-1252']
        suffix = self.ctx.input.match.suffix

        if suffix == ".gz":
            opener = lambda: gzip.open(self.ctx.input.match, 'rb')
        elif suffix == ".xz":
            opener = lambda: lzma.open(self.ctx.input.match, 'rb')
        else:
            opener = lambda: open(self.ctx.input.match, 'rb')

        reported = False
        try:
            with opener() as input_file:
                for raw in input_file:
                    for encoding in encodings:
                        try:
                            yield raw.decode(encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        # No candidate encoding fits: keep the line rather than
                        # dropping evidence, with undecodable bytes replaced.
                        if not reported:
                            logger.warning(
                                f"Undecodable bytes in {self.ctx.input.match}, "
                                f"falling back to lossy decoding"
                            )
                            reported = True
                        yield raw.decode('utf-8', errors='replace')
        except OSError as exc:
            logger.error(f"Failed to read '{self.ctx.input.match}': {exc}")

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
        try:
            if not output_path:
                output_path = self.ctx.output.output_file

            with open(output_path, "a", encoding='utf-8') as file:  # ouvert une seule fois
                while True:
                    data = queue.get()
                    if data is None:
                        queue.task_done()
                        break
                    try:
                        json.dump(data, file)
                        file.write('\n')
                    finally:
                        queue.task_done()

        except Exception as exc:
            logger.error_handler(exc)

    def start_writer_thread(self, output_path=None):
        """
        Starts a writer thread that will handle saving data to JSONL files.

        Returns:
            Queue: A queue that will hold data to be processed by the writer thread.
        """
        # TODO : SET THIS VALUE IN A CONFIG FILE
        MAX_QUEUE_SIZE = 100000
        q = queue.Queue(maxsize=MAX_QUEUE_SIZE)
        writer_thread = threading.Thread(target=self._thread_save_jsonl, args=(q, output_path))
        writer_thread.start()

        if not hasattr(self, '_writer_threads'):
            self._writer_threads = []
        self._writer_threads.append((q, writer_thread))

        return q

    def close_writer_threads(self, timeout: float = 30.0):
        """
        Guarantees every writer thread started by this module terminates.

        Prevents agent hangs when a module fails mid-parse by ensuring 
        the writer thread receives its termination and shuts down cleanly.

        Args:
            timeout (float): Seconds to wait for each writer thread to finish.
        """
        for q, thread in getattr(self, '_writer_threads', []):
            if not thread.is_alive():
                continue
            try:
                # Harmless when the module already sent one: nothing reads it.
                q.put_nowait(None)
            except queue.Full:
                logger.warning("Writer queue full while shutting down, forcing drain")
                try:
                    while not q.empty():
                        q.get_nowait()
                        q.task_done()
                    q.put_nowait(None)
                except (queue.Empty, queue.Full, ValueError):
                    pass
            thread.join(timeout)
            if thread.is_alive():
                logger.error(f"Writer thread did not stop within {timeout}s")
        self._writer_threads = []

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
        if not match:
            return None
        return match.group(1) if match.groups() else match.group(0)

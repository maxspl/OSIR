from contextlib import contextmanager
import logging
import io
import json
import os
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()


@contextmanager
def capture_log_output(target_logger):
    """
        Temporarily captures log emissions from a specific logger into an in-memory buffer.

        In the OSIR orchestration flow, this context manager is used to intercept 
        module-specific logs (DEBUG, INFO, ERROR) so they can be saved into 
        the task trace database. This provides a granular view of what happened 
        during a specific forensic execution without cluttering the main system log.

        Args:
            target_logger (logging.Logger): The logger instance to intercept.

        Yields:
            io.StringIO: A string buffer containing the captured log data.
    """
    log_capture_string = io.StringIO()
    temp_handler = logging.StreamHandler(log_capture_string)
    db_fmt = logging.Formatter('[%(levelname)s][%(asctime)s] - %(filename)s:%(lineno)d - %(funcName)s - %(message)s')
    temp_handler.setFormatter(db_fmt)
    target_logger.addHandler(temp_handler)
    try:
        yield log_capture_string
    finally:
        target_logger.removeHandler(temp_handler)


def normalize_osir_path(input_path: str) -> str:
    """
        Standardizes paths to be relative to the framework's internal share mount point.

        Args:
            input_path (str): The absolute or prefixed path to normalize.

        Returns:
            str: The normalized path starting from /OSIR/share.
    """
    anchor = "/OSIR/share"

    if anchor in str(input_path):
        s_path = str(input_path)
        return s_path[s_path.find(anchor):]

    return input_path


def get_latest_log_by_task_id(target_task_id: str, file_path: str = "/OSIR/share/log/task_traces.jsonl"):
    """
        Retrieves the most recent log trace for a specific Task ID by reading the log file in reverse.

        Args:
            target_task_id (str): The unique identifier of the forensic task.
            file_path (str): The path to the JSONL trace file.

        Returns:
            dict: The parsed JSON trace object if found, None otherwise.
    """
    if not os.path.exists(file_path):
        return None

    with open(file_path, 'rb') as f:
        try:
            # Move the pointer to the very end of the file
            f.seek(0, os.SEEK_END)
            pointer = f.tell()
            buffer = bytearray()

            while pointer > 0:
                pointer -= 1
                f.seek(pointer)
                char = f.read(1)

                # Check if we hit a newline or the start of the file
                if char == b'\n' and buffer:
                    # Decode and validate the JSON line
                    line = buffer[::-1].decode('utf-8')
                    trace = json.loads(line)
                    if trace.get("task_id") == target_task_id:
                        return trace  # Found the most recent entry, stop search
                    buffer = bytearray()
                elif char != b'\n':
                    buffer.extend(char)

            # Verification for the first line of the file (no leading newline)
            if buffer:
                line = buffer[::-1].decode('utf-8')
                trace = json.loads(line)
                if trace.get("task_id") == target_task_id:
                    return trace

        except Exception as e:
            logger.error(f"Reverse log read error: {e}")

    return None


def remove_placeholders(text: str) -> str:
    """
    Replaces all placeholders {key} with an empty string.
    
    Args:
        text: The text containing placeholders
        
    Returns:
        The text without placeholders
    """
    import re
    return re.sub(r'\{[^}]+\}', '', text)
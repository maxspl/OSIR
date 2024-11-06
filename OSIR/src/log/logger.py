# File: src/log/logger.py
import logging
import os
import traceback


class AppLogger:
    """
    Manages and provides logging capabilities for application-wide use.
    """
    def __init__(self, name=__name__, log_file='OSIR.log'):
        """
        Initializes the logger with console and file handlers.
        The log file will be located relative to this script's location.

        Args:
            name (str): Name of the logger.
            log_file (str): Filename for the log file.
        """
        # Set up a dynamic path for the log file that is relative to this script's directory
        directory = os.path.dirname(__file__)  # Gets the directory of the current script (logger.py)
        log_directory = os.path.join(directory, '..', '..', 'log')
        relative_path = os.path.join(directory, '..', '..', 'log', log_file)
        # FIX FILE NOT EXIST
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        absolute_path = os.path.abspath(relative_path)  # Converts to absolute path (removes ../../)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Setting the threshold of logger to DEBUG

        # Create handlers
        c_handler = logging.StreamHandler()  # Console handler
        f_handler = logging.FileHandler(absolute_path)  # File handler with dynamic path

        # Set levels for handlers
        c_handler.setLevel(logging.DEBUG)  # Console handler level
        f_handler.setLevel(logging.DEBUG)  # File handler level

        # Create formatters and add it to handlers
        c_format = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
        f_format = logging.Formatter('[%(levelname)s] - %(asctime)s - %(name)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        self.logger.addHandler(c_handler)
        self.logger.addHandler(f_handler)

    def get_logger(self):
        """
        Retrieves the logger instance associated with this AppLogger.

        Returns:
            logging.Logger: The logger instance configured for the application.
        """
        return self.logger

    def error_handler(self, fct_name, ex, msg=""):
        if msg:
            self.logger.error(msg)
        self.logger.error(str('Module : \'{}\', Error is : {}'.format(fct_name, str(ex))))
        self.logger.error(str('Exception Traceback: {}'.format(traceback.format_exc())))

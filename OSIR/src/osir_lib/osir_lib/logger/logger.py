import logging
import os
import sys
import threading
import traceback
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.core.OsirSingleton import singleton


class CustomLogger(logging.getLoggerClass()):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

    def error_handler(self, ex: Exception, message="", *args, **kwargs):
        # Capture the traceback and extract file name and line number
        tb_str = traceback.extract_tb(ex.__traceback__)
        fn, lno, func, sinfo = self.findCaller(stack_info=False, stacklevel=2)
        if tb_str:
            # Get the last entry from the traceback
            last_entry = tb_str[-1]
            filename = last_entry.filename
            lineno = last_entry.lineno
            # Format file name and line number
            location_info = f"{filename}:{lineno}"
            # Log the error message with location info
            if message:
                self._log(logging.ERROR, f"Message: {message}", args, **kwargs, extra={'caller': (fn, lno, func, sinfo)})

            self._log(logging.ERROR, f"Error: {ex}", args, **kwargs,
                      extra={'caller': (fn, lno, func, sinfo)})
            self._log(logging.ERROR, f"Location: \033[1;35m {location_info} \033[0m", args, **kwargs,
                      extra={'caller': (fn, lno, func, sinfo)})
            self._log(logging.ERROR, str('Traceback: {}'.format(traceback.format_exc())), args, **kwargs,
                      extra={'caller': (fn, lno, func, sinfo)})
        else:
            self._log(logging.ERROR, f"Error: {ex}", args, **kwargs,
                      extra={'caller': (fn, lno, func, sinfo)})
            self._log(logging.ERROR, str('Traceback: {}'.format(traceback.format_exc())), args, **kwargs,
                      extra={'caller': (fn, lno, func, sinfo)})


class LevelBasedHandler(logging.StreamHandler):
    def __init__(self, level_formatter_map, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level_formatter_map = level_formatter_map

    def emit(self, record):
        default_formatter = logging.Formatter(
            '[%(levelname)s] %(filename)s:%(lineno)d - %(funcName)s() - %(message)s'
        )
        formatter = self.level_formatter_map.get(record.levelno, default_formatter)
        self.setFormatter(formatter)
        super().emit(record)


class LogFormatter(logging.Formatter):

    COLOR_CODES = {
        logging.CRITICAL: "\033[0;95m",  # bright/bold magenta
        logging.ERROR:    "\033[0;91m",  # bright/bold red
        logging.WARNING:  "\033[0;93m",  # bright/bold yellow
        logging.INFO:     "\033[0;94m",  # white / light gray
        logging.DEBUG:    "\033[0;96m"   # bright/bold black / dark gray
    }

    RESET_CODE = "\033[0m"
    ORIGIN_COLOR = "\033[1;36m"

    def __init__(self, color, *args, **kwargs):
        super(LogFormatter, self).__init__(*args, **kwargs)
        self.color = color

    def format(self, record, *args, **kwargs):
        # Ajout des informations du lieu d'appel dans le message de log
        task_id = getattr(record, 'task_id', None)
        record.task_id_str = f"[TASK:{task_id}]" if task_id else ""
        origin = getattr(record, 'origin', 'UNKNOWN')
        record.origin_str = f"{self.ORIGIN_COLOR}[{origin:^8s}]{self.RESET_CODE}"
        filename_lineno = f"{record.filename}:{record.lineno}"
        record.filename_lineno = f"{filename_lineno:^25.25}"
        record.funcName = record.funcName+'()'
        record.funcName = f"{record.funcName:^25.25}"

        if hasattr(record, 'caller'):
            fn, lno, func, sinfo = record.caller
            record.msg = f"{record.msg}"
            record.filename = fn
            record.lineno = lno
            record.funcName = func
        if (self.color is True and record.levelno in self.COLOR_CODES):
            record.color_on = self.COLOR_CODES[record.levelno]
            record.color_off = self.RESET_CODE
        else:
            record.color_on = ""
            record.color_off = ""
        return super(LogFormatter, self).format(record, *args, **kwargs)


@singleton
class AppLogger:
    def __init__(self, name=__name__, log_file='OSIR.log') -> None:
        logging.setLoggerClass(CustomLogger)
        sys.excepthook = self.handle_uncaught_exception
        threading.excepthook = self.handle_thread_exception
        
        # Define formatters for DEBUG and INFO levels
        debug_formatter = LogFormatter(fmt='%(color_on)s[DEBUG] %(filename_lineno)s %(color_off)s - %(funcName)-25s - %(message)s ', color=True)
        warning_formatter = LogFormatter(fmt='%(color_on)s[WARNING] %(filename_lineno)s %(color_off)s - %(funcName)-25s - %(message)s ', color=True)

        info_formatter = LogFormatter(fmt='%(color_on)s[INFO] %(filename_lineno)s %(color_off)s - %(funcName)-25s - %(message)s ', color=True)
        critical_formatter = LogFormatter(fmt='%(color_on)s[CRITICAL] %(filename_lineno)s - %(funcName)-25s - %(message)s %(color_off)s', color=True)
        error_formatter = LogFormatter(fmt='%(color_on)s[ERROR] %(filename_lineno)s %(color_off)s - %(funcName)-25s - %(message)s ', color=True)

        # default_formatter = logging.Formatter(
        #     '[%(levelname)s] [%(asctime)s] - %(filename)s:%(lineno)d - %(message)s'
        # )

        # Create and configure the logger
        self.logger = logging.getLogger('customLogger')

        self.logger.setLevel(logging.DEBUG)  # Capture all messages at or above DEBUG level

        # Define formatters for file handlers
        file_debug_formatter = logging.Formatter(
            '[%(origin_str)s]%(task_id_str)s[%(levelname)s][%(asctime)s] - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
        )

        # Create custom handlers for console logging
        console_level_formatter_map = {
            logging.DEBUG: debug_formatter,
            logging.INFO: info_formatter,
            logging.ERROR: error_formatter,
            logging.WARNING: warning_formatter,
            logging.CRITICAL: critical_formatter

        }
        console_handler = LevelBasedHandler(console_level_formatter_map)

        log_directory = OSIR_PATHS.LOG_DIR

        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        log_file = os.path.join(OSIR_PATHS.LOG_DIR, log_file)        

        # Create custom handlers for file logging
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_debug_formatter)  # Default formatter for all levels

        # Add handlers to the logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

    def handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """Gère les exceptions non capturées dans le thread principal."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.logger.error(
            f"Uncaught exception: {exc_value}",
            exc_info=(exc_type, exc_value, exc_traceback),
            extra={'origin': 'UNCAUGHT'}
        )

    def handle_thread_exception(self, args):
        """Gère les exceptions non capturées dans les threads."""
        exc_type, exc_value, exc_traceback, thread = (
            args.exc_type, args.exc_value, args.exc_traceback, args.thread
        )
        if exc_type is SystemExit:
            return
        self.logger.error(
            f"Uncaught exception in thread {thread.name}: {exc_value}",
            exc_info=(exc_type, exc_value, exc_traceback),
            extra={'origin': f'THREAD-{thread.name}'}
        )

# MASTER_LOGGER = logging.LoggerAdapter(AppLogger().get_logger(), {'origin': 'MASTER'})
# AGENT_LOGGER = logging.LoggerAdapter(AppLogger().get_logger(), {'origin': 'AGENT'})
# API_LOGGER = logging.LoggerAdapter(AppLogger().get_logger(), {'origin': 'API'})
# CLIENT_LOGGER = logging.LoggerAdapter(AppLogger().get_logger(), {'origin': 'CLIENT'})

# Example usage of the imported custom logger with custom function
# logger.debug("This is a debug message from main.py")
# logger.info("This is an info message from main.py")
# logger.warning("This is a warning message from main.py")
# logger.error("This is an error message from main.py")
# logger.critical("This is a critical message from main.py")

# # Using the custom log method
# logger.custom_log("This is a custom log message from main.py")

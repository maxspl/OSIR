from datetime import datetime
import functools
import inspect
from io import StringIO
import io
import json
import logging
import os
import threading
import time
from typing import Any, Callable, Optional
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.logger import AppLogger
from osir_service.postgres.PostgresConstants import ProcessingStatus

logger = AppLogger().get_logger()


def timeit(func):
    """
        Decorator that measures and logs the execution time of a specific function.

        Args:
            func (Callable): The function whose execution time is to be measured.

        Returns:
            Callable: The wrapped function with performance logging enabled.
    """
    def timeit_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        AppLogger().get_logger().debug(f"Function \033[1;35m {func.__name__} \033[0m took \033[1;35m {execution_time:.4f} \033[0m seconds to execute")
        return result
    return timeit_wrapper


def pinfo(func):
    """
        Decorator to log the lifecycle of file processing within an OSIR module.

        Args:
            func (Callable): The processing function to be wrapped.

        Returns:
            Callable: The wrapped function with start/end logging for the input file.
    """

    def wrapper(self, *args, **kwargs):
        file = self.module.input.file
        AppLogger().get_logger().debug(f"Processing file {file}")

        result = func(self, *args, **kwargs)

        AppLogger().get_logger().debug(f"Processing done")
        return result
    return wrapper


def osir_internal_module(cls_or_func=None, *, trace: Optional[bool] = True):
    """
        Core OSIR decorator for internal modules that automates task state and logging.

        Args:
            cls_or_func (Any): The class or function representing the internal module.
            trace (bool): Whether to capture and persist logs to the database.

        Returns:
            Callable: The decorated module ready for the OSIR task dispatcher.
    """
    def decorator(cls_or_func: Any):
        @functools.wraps(cls_or_func)
        def wrapper(**available_vars):
            # 1. Extraction and cleanup of task_id to prevent signature mismatch
            task_id = available_vars.get('task_id')

            # 2. Configure in-memory log capture
            log_capture = io.StringIO()
            capture_handler = logging.StreamHandler(log_capture)
            db_fmt = logging.Formatter('[%(levelname)s][%(asctime)s] - %(filename)s:%(lineno)d - %(funcName)s - %(message)s')
            capture_handler.setFormatter(db_fmt)

            # Attach capture handler to the main logger
            main_logger = AppLogger().get_logger()
            main_logger.addHandler(capture_handler)

            start_time = datetime.now()
            status = ProcessingStatus.PROCESSING_DONE

            # 3. Prepare parameters for the target function or class
            target = cls_or_func if inspect.isfunction(cls_or_func) else cls_or_func.__init__
            sig = inspect.signature(target)

            # Pass only arguments that the target function is prepared to accept
            kwargs_to_pass = {
                k: v for k, v in available_vars.items()
                if k in sig.parameters
            }

            try:
                # 4. Execution logic
                if isinstance(cls_or_func, type):
                    instance = cls_or_func(**kwargs_to_pass)
                    result = instance() if hasattr(instance, '__call__') else instance
                else:
                    result = cls_or_func(**kwargs_to_pass)

                if result is False:
                    status = ProcessingStatus.PROCESSING_FAILED
                return result

            except Exception as e:
                status = ProcessingStatus.PROCESSING_FAILED
                main_logger.error(f"Execution Error: {str(e)}")
                raise e

            finally:
                # 5. Finalization and handler cleanup
                end_time = datetime.now()
                main_logger.removeHandler(capture_handler)

                if trace and task_id:
                    logs_text = log_capture.getvalue()
                    finalize_task(status, task_id, cls_or_func.__name__, start_time, end_time, logs_text)
                elif task_id:
                    finalize_task(status, task_id, cls_or_func.__name__, start_time, end_time, "Function not traced")
        wrapper.__osir_internal__ = True
        return wrapper

    if cls_or_func is None:
        return decorator
    return decorator(cls_or_func)


def trace_func():
    """
        Decorator used to capture function output and update the task status in the DB.

        Returns:
            Callable: The decorated function with full database tracing.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Intercept and Remove task_id from kwargs to avoid crashing target function
            task_id = kwargs.pop('task_id', None)

            # Setup logging capture
            log_capture = StringIO()
            capture_handler = logging.StreamHandler(log_capture)
            db_fmt = logging.Formatter('[%(levelname)s][%(asctime)s] - %(filename)s:%(lineno)d - %(funcName)s - %(message)s')
            capture_handler.setFormatter(db_fmt)

            # Use the existing AppLogger
            main_logger = AppLogger(__name__).get_logger()
            main_logger.addHandler(capture_handler)

            start_time = datetime.now()
            status = ProcessingStatus.PROCESSING_DONE

            try:
                # 2. Execute the function with cleaned arguments
                result = func(*args, **kwargs)

                if result is False:
                    status = ProcessingStatus.PROCESSING_FAILED
                return result

            except Exception as e:
                status = ProcessingStatus.PROCESSING_FAILED
                main_logger.error(f"Execution Error: {str(e)}")
                raise e

            finally:
                if logger and capture_handler and task_id:
                    end_time = datetime.now()
                    logger.removeHandler(capture_handler)
                    logs_text = log_capture.getvalue()
                    finalize_task(status, task_id, func.__name__, start_time, end_time, logs_text)
        return wrapper
    return decorator


def finalize_task(status, task_id, func_name, start, end, logs):
    """
        Updates the PostgreSQL database with the final results and logs of a task.

        Args:
            status (ProcessingStatus): The final status (DONE or FAILED).
            task_id (int): The unique ID of the task in the database.
            func_name (str): The name of the module/function that executed.
            start (datetime): Execution start timestamp.
            end (datetime): Execution end timestamp.
            logs (str): The raw log output captured during execution.
    """
    from osir_service.postgres.PostgresService import DbOSIR

    db = DbOSIR()

    log_blob = {
        "function": func_name,
        "duration_seconds": (end - start).total_seconds(),
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "logs": logs.strip().split('\n')
    }

    db.task.update(
        task_id=task_id,
        processing_status=status,
        trace_data=log_blob
    )

    db.close()

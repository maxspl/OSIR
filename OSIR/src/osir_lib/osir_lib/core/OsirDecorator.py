from datetime import datetime
import functools
import inspect
from io import StringIO
import json
import logging
import os
import threading
import time
from typing import Any, Callable, Optional
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.logger import AppLogger
from osir_lib.logger import AppLogger
from osir_service.postgres.PostgresConstants import ProcessingStatus

logger = AppLogger().get_logger()

"""
    Measures the execution time of a function and logs it.

    Args:
        func (Callable): The function whose execution time is to be measured.

    Returns:
        Callable: The wrapped function with timing and logging enabled.
"""
def timeit(func):
    def timeit(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        AppLogger().get_logger().debug(f"Function \033[1;35m {func.__name__} \033[0m took \033[1;35m {execution_time:.4f} \033[0m seconds to execute")
        return result
    return timeit

"""
    Logs the start and end of a file processing function.

    Args:
        func (Callable): The function that processes the file.

    Returns:
        Callable: The wrapped function with logging for file processing.
"""
def pinfo(func):
    def wrapper(self, *args, **kwargs):
        file = self.module.input.file
        AppLogger().get_logger().debug(f"Processing file {file}")
        
        result = func(self, *args, **kwargs)
     
        AppLogger().get_logger().debug(f"Processing done")
        return result
    return wrapper

def osir_internal_module(cls_or_func=None, *, trace: Optional[bool] = True):
    def decorator(cls_or_func: Any):
        @functools.wraps(cls_or_func)
        def wrapper(**available_vars):
            task_id = available_vars.get('task_id', 'UNKNOWN')
            log_capture = None
            capture_handler = None
            logger = None
            start_time = datetime.now()

            if trace:
                log_capture = StringIO()
                capture_handler = logging.StreamHandler(log_capture)
                db_fmt = logging.Formatter('[%(levelname)s][%(asctime)s] - %(filename)s:%(lineno)d - %(funcName)s - %(message)s')
                capture_handler.setFormatter(db_fmt)
                
                logger = AppLogger().get_logger()
                logger.addHandler(capture_handler)
                
                # Création de l'adapter pour injecter le contexte
                adapter = logging.LoggerAdapter(logger, {'origin': "Agent", 'task_id': task_id})
                if 'logger' in (cls_or_func.__init__.__code__.co_varnames if isinstance(cls_or_func, type) else cls_or_func.__code__.co_varnames):
                    available_vars['logger'] = adapter

            target = cls_or_func if inspect.isfunction(cls_or_func) else cls_or_func.__init__
            sig = inspect.signature(target)
            
            kwargs_to_pass = {
                k: v for k, v in available_vars.items() 
                if k in sig.parameters
            }

            try:
                if isinstance(cls_or_func, type):
                    instance = cls_or_func(**kwargs_to_pass)
                    result = instance() if hasattr(instance, '__call__') else instance
                else:
                    result = cls_or_func(**kwargs_to_pass)
                return result

            except Exception as e:
                raise e

            finally:
                if trace and logger and capture_handler:
                    end_time = datetime.now()
                    logger.removeHandler(capture_handler)
                    logs_text = log_capture.getvalue()
                    
                    threading.Thread(
                        target=finalize_task,
                        args=(task_id, cls_or_func.__name__, start_time, end_time, logs_text),
                        daemon=True
                    ).start()

        # Marqueur interne Osir
        wrapper.__osir_internal__ = True
        return wrapper

    if cls_or_func is None:
        return decorator
    else:
        return decorator(cls_or_func)

def trace_func():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Intercept and Remove task_id from kwargs
            # We "pop" it so it doesn't exist when we call func(**kwargs)
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
            status = "processing_done"

            try:
                # 2. Execute the function with the cleaned kwargs
                # task_id is no longer in kwargs, so run(self) won't crash
                result = func(*args, **kwargs)
                
                if result is False:
                    status = "processing_failed"
                return result

            except Exception as e:
                status = "processing_failed"
                main_logger.error(f"Execution Error: {str(e)}")
                raise e

            finally:
                if logger and capture_handler and task_id:
                    end_time = datetime.now()
                    logger.removeHandler(capture_handler)
                    logs_text = log_capture.getvalue()
                    
                    threading.Thread(
                        target=finalize_task,
                        args=(task_id, func.__name__, start_time, end_time, logs_text),
                        daemon=True
                    ).start()
        return wrapper
    return decorator

def finalize_task(task_id, func_name, start, end, logs):
    from osir_service.postgres.PostgresService import OSIR_DB

    # 1. On prépare le dictionnaire (le "blob")
    log_blob = {
        "function": func_name,
        "duration_seconds": (end - start).total_seconds(),
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "logs": logs.strip().split('\n')
    }

    # 2. On met à jour la base de données
    OSIR_DB.task.update(
        task_id=task_id,
        processing_status=ProcessingStatus.PROCESSING_DONE,
        trace_data=log_blob
    )

# def save_to_jsonl(task_id, func_name, start, end, logs):
    
    # """Enregistre les détails de l'exécution dans un fichier JSONL."""
    
    # # 1. Préparation du dictionnaire de données
    # log_data = {
    #     "timestamp": datetime.now().isoformat(),
    #     "task_id": task_id,
    #     "function": func_name,
    #     "duration_seconds": (end - start).total_seconds(),
    #     "start_time": start.isoformat(),
    #     "end_time": end.isoformat(),
    #     "logs": logs.strip().split('\n'), # On transforme les logs en liste pour un JSON propre
    # }

    # # 2. Définition du chemin du fichier
    # # On le place dans ton répertoire log habituel
    # log_dir = OSIR_PATHS.LOG_DIR
    
    # jsonl_path = os.path.join(log_dir, "task_traces.jsonl")

    # try:
    #     # 3. Écriture en mode 'append' (a)
    #     with open(jsonl_path, 'a', encoding='utf-8') as f:
    #         f.write(json.dumps(log_data, ensure_ascii=False) + '\n')
            
    #     # On garde un petit debug console pour savoir que c'est fait        
    # except Exception as e:
    #     logger.error(f"Failed to write JSONL: {e}")

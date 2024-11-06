import time
from src.log.logger_config import AppLogger

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
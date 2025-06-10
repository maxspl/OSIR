from os import environ
from src.utils.BaseModule import BaseModule
import pickle
from celery import Celery
from celery import signature
from src.log.logger_config import AppLogger
import os

logger = AppLogger(__name__).get_logger()


def run_task(case_path, module_data, task, queue, case_uuid):
    """
    Submits a task for asynchronous execution using Celery, specifying the task's parameters and execution queue.

    Args:
        case_path (str): The base directory path where the case files are stored and operations will be performed.
        module_data (bytes): Serialized data of the module instance to be processed in the task.
        task (str): The name of the task function to execute.
        queue (str): The name of the Celery queue in which the task should be enqueued.
        case_uuid (str): A unique identifier for the case associated with the task.

    Environment Variables:
        CELERY_BROKER_URL (str): The URL of the Celery message broker.
        CELERY_RESULT_BACKEND (str): The URL of the backend used to store task results.
    """
    module_instance: BaseModule = pickle.loads(module_data)
    if module_instance.input.dir: 
        input = module_instance.input.dir
    elif module_instance.input.file: 
        input = module_instance.input.file
    else:
        input = ""

    logger.debug(f"""Task Pushed : \n
                Task Name : {task} \n
                Case Path : {case_path} \n
                Input : {input} \n
                Case UUID : {case_uuid} \n""")
    
    RABBITMQ_USER = os.getenv('RABBITMQ_DEFAULT_USER', 'missing RABBITMQ_DEFAULT_USER env var')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_DEFAULT_PASS', 'missing RABBITMQ_DEFAULT_PASS env var')
    CELERY_BROKER_URL = environ.get('CELERY_BROKER_URL', f'pyamqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@master-rabbitmq:5672//')
    CELERY_RESULT_BACKEND = environ.get('CELERY_RESULT_BACKEND', 'redis://master-redis:6379/0')

    Celery(name='OSIR', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
    task_signature = signature(task, args=(input, case_path, module_data, case_uuid), immutable=True, queue=queue)
    result = task_signature.apply_async()
    logger.debug(f"task id : {result.id}")
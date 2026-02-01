import os

from os import environ
import uuid
from celery import Celery
from celery import signature

from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_lib.logger import AppLogger
from osir_service.postgres.PostgresService import DbOSIR

logger = AppLogger(__name__).get_logger()


class TaskService:
    def __init__(self):
        pass

    @staticmethod
    def get_task_name(module: OsirModuleModel):
        if "internal" in module.processor_type:
            return "internal_processor_task"
        else:
            return "external_processor_task"

    @staticmethod
    def get_queue_name(module: OsirModuleModel):
        if module.disk_only and module.no_multithread:
            return f"{module.processor_os}_no_multithread_disk_only"
        elif module.disk_only:
            return f"{module.processor_os}_multithread_disk_only"
        elif module.no_multithread:
            return f"{module.processor_os}_no_multithread"
        else:
            return f"{module.processor_os}_multithread"

    @staticmethod
    def push_task(case_path, module_instance: OsirModuleModel, case_uuid, handler_uuid):
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
        if not module_instance.input.match:
            if module_instance.input.type == "file":
                module_instance.input.match = module_instance.input.file
            else:
                module_instance.input.match = module_instance.input.dir

        RABBITMQ_USER = os.getenv('RABBITMQ_DEFAULT_USER', 'missing RABBITMQ_DEFAULT_USER env var')
        RABBITMQ_PASSWORD = os.getenv('RABBITMQ_DEFAULT_PASS', 'missing RABBITMQ_DEFAULT_PASS env var')
        CELERY_BROKER_URL = environ.get('CELERY_BROKER_URL', f'pyamqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@master-rabbitmq:5672//')
        CELERY_RESULT_BACKEND = environ.get('CELERY_RESULT_BACKEND', 'redis://master-redis:6379/0')

        Celery(name='OSIR', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

        task_signature = signature(
            TaskService.get_task_name(module_instance),
            args=(module_instance.input.match, case_path, module_instance.model_dump_json(), case_uuid),
            immutable=True,
            queue=TaskService.get_queue_name(module_instance)
        )
        custom_task_id = str(uuid.uuid4())
        db = DbOSIR()
        db.task.create(
            task_id=custom_task_id,
            case_uuid=case_uuid,
            agent="Null",
            module=module_instance.module_name,
            input=module_instance.input.match
        )

        db.handler.append_task_ids(
            handler_id=handler_uuid,
            new_task_ids=[custom_task_id]
        )
        db.close()
        result = task_signature.apply_async(task_id=custom_task_id)

        logger.info(f"""Task Pushed : \n
                    Task Name : {module_instance.module_name} \n
                    Task ID : {result.id} \n
                    Task Type : {module_instance.processor_type} \n
                    Case Path : {case_path} \n
                    Input : {module_instance.input.match} \n
                    Case UUID : {case_uuid} \n""")

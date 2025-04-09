import multiprocessing
import sys
import signal
import pickle
import copy
import os
import time
from celery import Celery
from os import environ, cpu_count
from src.log.logger_config import AppLogger
from src.processor import InternalProcessor
from src.processor import ExternalProcessor
from src.utils.BaseModule import BaseModule
from src.utils.DbOSIR import DbOSIR
from src.utils.AgentConfig import AgentConfig

logger = AppLogger().get_logger()


class CeleryWorker:
    """
    Manages a Celery worker that handles task execution in a distributed environment, supporting different processing
    modes based on the configuration and environment.
    """
    def __init__(self):
        """
        Initializes the Celery worker by setting up the broker and backend configurations, queues, and registering task handlers.
        """
        self.logger = AppLogger(__name__).get_logger()
        self.agent_config = AgentConfig()
        # if self.agent_config.get_master_details()['host'] in ["127.0.0.1", "localhost"]:
        if self.agent_config.standalone:
            self.master_host = "host.docker.internal"  # Agent cannot use localhost to communicate with other docker
        else:
            self.master_host = self.agent_config.master_host

        RABBITMQ_USER = os.getenv('RABBITMQ_DEFAULT_USER', 'missing RABBITMQ_DEFAULT_USER env var')
        RABBITMQ_PASSWORD = os.getenv('RABBITMQ_DEFAULT_PASS', 'missing RABBITMQ_DEFAULT_PASS env var')

        self.CELERY_BROKER_URL = environ.get('CELERY_BROKER_URL', f'pyamqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{self.master_host}:5672//')
        self.CELERY_RESULT_BACKEND = environ.get('CELERY_RESULT_BACKEND', f'redis://{self.master_host}:6379/0')

        self.app = Celery(name='OSIR', backend=self.CELERY_RESULT_BACKEND)
        self.app.conf.update(
            broker_url=self.CELERY_BROKER_URL,
            result_backend=self.CELERY_RESULT_BACKEND,
            resultrepr_maxsize=5000000,
            result_extended=True,
            task_track_started=True,  # Enable tracking
            task_send_sent_event=True  # Enable events

        )
        self.app.amqp.argsrepr_maxsize = 10000

        self._register_tasks()

    def _is_item_in_use(self, case_uuid, module_instance):
        """
        Wait until the input file or directory is free to use, i.e., not being used by another module.

        Args:
            case_uuid (str): The UUID of the case.
            module_instance: The module instance containing the input to be checked.

        Returns:
            None
        """
        if module_instance.input.type == "file":
            # file_opened = self._is_file_opened(module_instance.input.file)
            file_opened = self.DbOSIR.check_input_file(case_uuid, module_instance.input.file)
            while file_opened:
                logger.debug(f"{module_instance.module_name} - input file {module_instance.input.file} is opened by another module. Waiting...")
                time.sleep(3)
                file_opened = self.DbOSIR.check_input_file(case_uuid, module_instance.input.file)
        elif module_instance.input.type == "dir":
            file_opened = self.DbOSIR.check_input_dir(case_uuid, module_instance.input.dir)
            while file_opened:
                logger.debug(f"{module_instance.module_name} - input dir {module_instance.input.dir} is opened by another module. Waiting...")
                time.sleep(3)
                file_opened = self.DbOSIR.check_input_dir(case_uuid, module_instance.input.dir)

    def _is_file_being_written(self, module_instance, check_interval=0.5):
        """
        Check if a file is being written to by monitoring its size and modification time.

        Args:
            module_instance: The module instance containing the file to be checked.
            check_interval (float, optional): The interval in seconds to wait between checks. Default is 0.5 seconds.

        Returns:
            bool: True if the file size or modification time has changed, indicating it is being written to. False otherwise.
    """
        if module_instance.input.type == "file":
            file_path = module_instance.input.file
            try:
                # Get the initial size and modification time of the file
                initial_size = os.path.getsize(file_path)
                initial_mtime = os.path.getmtime(file_path)

                # Wait for the specified interval
                time.sleep(check_interval)

                # Get the size and modification time of the file again
                final_size = os.path.getsize(file_path)
                final_mtime = os.path.getmtime(file_path)

                # Determine if the file size or modification time has changed
                if initial_size != final_size or initial_mtime != final_mtime:
                    return True
                else:
                    return False
            except FileNotFoundError:
                logger.debug(f"File not found: {file_path}")
                return False
            except Exception as e:
                logger.debug(f"An error occurred: {e}")
                return False

    def _register_tasks(self):
        """
        Registers internal and external processing tasks with Celery, defining their behavior and exception handling.
        """
        @self.app.task(name="internal_processor_task")
        def task_internal_processor(input_dir, case_path, module_bytes, case_uuid):
            """ celery task - internal_processor  """
            try:
                module_instance: BaseModule = pickle.loads(module_bytes)
                processor = InternalProcessor.InternalProcessor(case_path, module_instance)

                # Open db
                self.DbOSIR = DbOSIR(self.master_host, module_name=module_instance.module_name)
                # Check if input_file is used by another module
                logger.debug("Check if input files/foles of module is in use...")
                self._is_item_in_use(case_uuid, module_instance)

                # Wait if file is currently beeing written
                file_written = self._is_file_being_written(module_instance)
                while file_written:
                    logger.debug(f"{module_instance.module_name} - file {module_instance.input.file} is opened. Waiting...")
                    time.sleep(0.1)
                    file_written = self._is_file_being_written(module_instance)
                module_instance_cp = copy.deepcopy(module_instance)  # Must use a copy as internal processor can modify input_file
                if processor.available:
                    logger.debug(f"Running internal module {module_instance.module_name}.py")
                    self.DbOSIR.update_record(module_instance_cp, "processing_started", case_uuid)
                processor.run_module()
                self.DbOSIR.update_record(module_instance_cp, "processing_done", case_uuid)
                self.DbOSIR.close()
                return "internal_processor done"
            except Exception as exc:
                logger.error_handler(exc)
                # logger.erro(f"fail run the task. Error {str(e)}")

        @self.app.task(name="external_processor_task")
        def task_external_processor(input_dir, case_path, module_bytes, case_uuid):
            """ celery task - external_processor  """
            try:
                module_instance: BaseModule = pickle.loads(module_bytes)
                processor = ExternalProcessor.ExternalProcessor(case_path, module_instance)

                # Open db
                self.DbOSIR = DbOSIR(self.master_host, module_name=module_instance.module_name)

                # Check if input_file is used by another module
                logger.debug(f"check if input of {module_instance.module_name} is in use...")
                self._is_item_in_use(case_uuid, module_instance)

                # Wait if file is currently beeing written
                file_written = self._is_file_being_written(module_instance)
                while file_written:
                    logger.debug(f"{module_instance.module_name} - file {module_instance.input.file} is opened. Waiting...")
                    time.sleep(0.1)
                    file_written = self._is_file_being_written(module_instance)

                self.DbOSIR.update_record(module_instance, "processing_started", case_uuid)
                processor.run_module()
                self.DbOSIR.update_record(module_instance, "processing_done", case_uuid)
                self.DbOSIR.close()
                return "external_processor done"
            except Exception as e:
                logger.debug(f"fail run the task. Error {str(e)}")

    def _start_single_worker(self, argv):
        """
        Starts a single Celery worker with the given command-line arguments.

        Args:
            argv (list): A list of command-line arguments to configure the Celery worker.
        """
        self.app.worker_main(argv)

    def start_worker(self):
        """
        Starts multiple Celery workers based on system resources and configuration, managing different task queues for processing.
        """
        def signal_handler(sig, frame):
            print('Stopping worker...')
            sys.exit(0)

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        total_cores = cpu_count()
        # Define default concurrency for Windows and get custom value if provided
        default_windows_cores = 2
        try:
            windows_cores = int(os.getenv('WINDOWS_CORES', default_windows_cores))
        except Exception as exc:
            windows_cores = default_windows_cores
            logger.error(exc)

        host_hostname = os.getenv('HOST_HOSTNAME', '%h')  # Default to '%h' if the env var is not set

        # Define the arguments for the required workers
        worker_configs = [
            {
                'hostname': f'unix_worker_no_multithread@{host_hostname}',
                'queue': 'unix_no_multithread',
                'autoscale': '1'  # Max 1 worker
            },
            {
                'hostname': f'unix_worker_multithread@{host_hostname}',
                'queue': 'unix_multithread',
                'autoscale': f'{total_cores},1'  # Max total_cores workers, min 2 workers
            },
            {
                'hostname': f'windows_worker_no_multithread@{host_hostname}',
                'queue': 'windows_no_multithread',
                'autoscale': '1'  # Max 1 worker
            },
            {
                'hostname': f'windows_worker_multithread@{host_hostname}',
                'queue': 'windows_multithread',
                'autoscale': f'{windows_cores},1'  # Dynamic max workers based on env, min 1 worker
            }
        ]

        if self.agent_config.standalone:
            worker_configs.extend([
                {
                    'hostname': f'unix_worker_no_multithread_disk_only@{host_hostname}',
                    'queue': 'unix_no_multithread_disk_only',
                    'autoscale': '1'  # Max 1 worker
                },
                {
                    'hostname': f'unix_worker_multithread_disk_only@{host_hostname}',
                    'queue': 'unix_multithread_disk_only',
                    'autoscale': f'{total_cores},2'  # Max total_cores workers, min 2 workers
                }
            ])

        processes = []

        for config in worker_configs:
            argv = [
                'worker',
                '--loglevel=info',
                f'--hostname={config["hostname"]}',
                '-Q', config['queue'],
                '--time-limit=36000',
                '-E',
                f'--autoscale={config["autoscale"]}',
                '--logfile=/OSIR/OSIR/log/celery.log'
            ]
            process = multiprocessing.Process(target=self._start_single_worker, args=(argv,))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()


# Example of instantiating and using the CeleryWorker class
if __name__ == "__main__":
    worker = CeleryWorker()
    worker.start_worker()

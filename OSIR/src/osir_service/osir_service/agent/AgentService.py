import json
import multiprocessing
import sys
import signal
import os
import time
from celery import Celery
from celery import current_task
from os import environ, cpu_count

from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.logger import AppLogger
from osir_lib.core.OsirModule import OsirModule
from osir_lib.core.OsirAgentConfig import OsirAgentConfig
from osir_lib.core.OsirUtils import capture_log_output
from osir_lib.core.OsirDecorator import pop_task_trace
from osir_service.orchestration.TaskProcessorService import InternalProcessor
from osir_service.orchestration.TaskProcessorService import ExternalProcessor
from osir_service.postgres.OsirDbConstants import ProcessingStatus
from osir_service.postgres.OsirDb import OsirDb

logger = AppLogger().get_logger()


class CeleryWorker:
    """
        Orchestrates distributed forensic task execution using Celery.

        This class manages the lifecycle of OSIR workers, handling communication 
        with RabbitMQ (broker) and Redis (backend).
    """

    def __init__(self):
        """
        Initializes the Celery worker by setting up the broker and backend configurations, queues, and registering task handlers.
        """
        self.agent_config = OsirAgentConfig()
        if self.agent_config.standalone:
            self.master_host = "host.docker.internal"  # Agent cannot use localhost to communicate with other docker
        else:
            self.master_host = self.agent_config.master_host

        RABBITMQ_USER = os.getenv('RABBITMQ_DEFAULT_USER', 'missing RABBITMQ_DEFAULT_USER env var')
        RABBITMQ_PASSWORD = os.getenv('RABBITMQ_DEFAULT_PASS', 'missing RABBITMQ_DEFAULT_PASS env var')
        POSTGRES_USER = os.getenv('POSTGRES_USER', 'missing POSTGRES_USER env var')
        POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'missing POSTGRES_PASSWORD env var')

        self.CELERY_BROKER_URL = environ.get('CELERY_BROKER_URL', f'pyamqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{self.master_host}:5672//')
        self.CELERY_RESULT_BACKEND = environ.get(
            'CELERY_RESULT_BACKEND',
            f'db+postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{self.master_host}:5432/OSIR_db'
        )

        self.app = Celery(name='OSIR', backend=self.CELERY_RESULT_BACKEND)
        self.app.conf.update(
            broker_url=self.CELERY_BROKER_URL,
            result_backend=self.CELERY_RESULT_BACKEND,
            resultrepr_maxsize=5000000,
            result_extended=True,
            task_track_started=True,  # Enable tracking
            task_send_sent_event=True,  # Enable events
            result_expires=None,  # No TTL purge: results are cleaned per-case
            database_short_lived_sessions=True,
        )
        self.app.amqp.argsrepr_maxsize = 10000

        self._register_tasks()
        self._local_count = 0

    def _is_item_in_use(self, case_uuid, module_instance: OsirModule, db: OsirDb, exclude_task_id=None):
        """
            Wait until the input file or directory is free to use, i.e., not being used by another module.

            Args:
                case_uuid (str): The UUID of the case.
                module_instance: The module instance containing the input to be checked.
                exclude_task_id (str, optional): The current task's id. With the
                    Celery result backend, the current task is already STARTED
                    when this runs, so it must be excluded from the check.

            Returns:
                None
        """
        if module_instance.input.match:
            # file_opened = self._is_file_opened(module_instance.input.file)
            file_opened = db.task.check_input(case_uuid, module_instance.input.match, exclude_task_id=exclude_task_id)
            while file_opened:
                logger.debug(f"{module_instance.module_name} - input {module_instance.input.match} is opened by another module. Waiting...")
                time.sleep(3)
                file_opened = db.task.check_input(case_uuid, module_instance.input.match, exclude_task_id=exclude_task_id)

    def _compute_parallel_capacity(self, standalone: bool, windows_cores: int):
        """
            Compute a safe global parallel budget based on available CPU resources,
            then split it across the different processing queues.

            Args:
                standalone (bool): Indicates whether standalone mode is enabled.
                windows_cores (int): The number of cores allocated to Windows processing.

            Returns:
                dict: A dictionary containing the computed capacities for:
                    - unix_parallel
                    - windows_parallel
                    - unix_disk_parallel
        """
        total_cores = max(1, cpu_count() or 1)

        reserve_serial_slots = 2          # unix_no_multithread + windows_no_multithread
        if standalone:
            reserve_serial_slots += 1     # unix_no_multithread_disk_only

        # CPU-based upper bound
        cpu_parallel_budget = max(1, total_cores - reserve_serial_slots)

        # Split budget between queues
        # Priority: unix multithread gets most of the budget, windows keeps a smaller controlled share.
        windows_parallel = min(max(1, windows_cores), max(1, cpu_parallel_budget // 3))
        remaining = max(1, cpu_parallel_budget - windows_parallel)

        if standalone:
            unix_parallel = max(1, int(remaining * 0.6))
            unix_disk_parallel = max(1, remaining - unix_parallel)
        else:
            unix_parallel = remaining
            unix_disk_parallel = 0

        logger.info(
            f"Worker capacity computed from host resources: "
            f"cores={total_cores}, "
            f"cpu_parallel_budget={cpu_parallel_budget}, "
            f"unix_parallel={unix_parallel}, "
            f"windows_parallel={windows_parallel}, "
            f"unix_disk_parallel={unix_disk_parallel}"
        )

        return {
            "unix_parallel": unix_parallel,
            "windows_parallel": windows_parallel,
            "unix_disk_parallel": unix_disk_parallel,
        }

    def _wait_for_input_stable(self, module_instance):
        """Wait only when a file input looks too recent or still changing.

        Watchdog already does a check for file in use but safety is kept here
        manually/API tasks.
        """
        if module_instance.input.type != "file":
            return

        file_path = module_instance.input.match
        stability_window = float(os.getenv("OSIR_FILE_STABILITY_WINDOW", "1.0"))
        check_interval = float(os.getenv("OSIR_FILE_STABILITY_CHECK_INTERVAL", "0.2"))
        max_wait = float(os.getenv("OSIR_FILE_STABILITY_MAX_WAIT", "300"))
        deadline = time.monotonic() + max_wait

        last_signature = None
        stable_since = None

        while True:
            try:
                st = os.stat(file_path)
            except FileNotFoundError:
                # Let the processor fail with its normal error path if the file
                # disappeared between task creation and execution.
                return

            size = int(st.st_size)
            mtime_ns = int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1_000_000_000)))
            signature = (size, mtime_ns)
            now = time.monotonic()

            # Fast path: no sleep for files that are already older than the
            # stability window.
            if time.time() - st.st_mtime >= stability_window:
                return

            if signature == last_signature:
                if stable_since is not None and now - stable_since >= stability_window:
                    return
            else:
                last_signature = signature
                stable_since = now

            if now >= deadline:
                logger.warning(
                    f"{module_instance.module_name} - file '{file_path}' did not become stable "
                    f"within {max_wait:.0f}s; processing anyway"
                )
                return

            logger.debug(
                f"{module_instance.module_name} - file '{file_path}' still looks recent/changing. Waiting..."
            )
            time.sleep(check_interval)

    def _register_tasks(self):
        """
        Registers internal and external processing tasks with Celery, defining their behavior and exception handling.
        """
        @self.app.task(name="internal_processor_task")
        def task_internal_processor(input_dir, case_path, module_bytes, case_uuid):
            """ celery task - internal_processor

                Task state lives in the Celery result backend: SUCCESS/FAILURE
                are reported by returning or raising, STARTED by
                task_track_started.
            """
            task_id = current_task.request.id
            worker_name = current_task.request.hostname

            try:
                # logger.debug(f"Task ID inside the task: {task_id}")
                module_dict = json.loads(module_bytes)
                module_dict['case_path'] = case_path
                module_instance = OsirModule.model_validate(module_dict)

                if module_instance.configuration.processor_os == 'windows' and not OsirAgentConfig().windows_configured:
                    raise RuntimeError(
                        f"Windows module '{module_instance.module_name}' cannot run on this agent: "
                        "Windows machine is not configured. Re-run agent setup and configure a Windows machine."
                    )

                processor = InternalProcessor(case_path, module_instance, task_id=task_id, agent_name=worker_name)
                logger.debug("Check if input files/foles of module is in use...")

                with OsirDb() as db:
                    if module_instance.output.type == 'multiple_files':
                        output_path = module_instance.output.dir
                    elif module_instance.output.type != 'None':
                        output_path = module_instance.output.file
                    else:
                        output_path = "N/A"

                    self._is_item_in_use(case_uuid, module_instance, db, exclude_task_id=task_id)
                    db.task.set_runtime_info(task_id, agent=worker_name, output=output_path)

                # Safety net for manually/API-pushed file tasks. The normal
                # watchdog path already delays unstable files before task push.
                self._wait_for_input_stable(module_instance)

                if processor.available:
                    impl_name = getattr(module_instance.configuration, "alt_module", None) or module_instance.module_name
                    logger.debug(
                        f"Running internal module '{module_instance.module_name}' "
                        f"using implementation '{impl_name}.py'"
                    )
                    processor.run_module()
            except Exception as exc:
                with capture_log_output(logger) as log_buffer:
                    logger.error_handler(exc)
                    captured_trace = log_buffer.getvalue()
                _, trace = pop_task_trace(task_id)
                module_logs = "\n".join(trace["logs"]) if trace else captured_trace.strip()
                # Re-raise so Celery records FAILURE + traceback (module logs
                # are chained into the stored traceback through the message).
                raise RuntimeError(f"internal_processor failed:\n{module_logs}") from exc

            status, trace = pop_task_trace(task_id)
            if status is ProcessingStatus.PROCESSING_FAILED:
                module_logs = "\n".join(trace["logs"]) if trace else "module returned False"
                raise RuntimeError(f"internal_processor failed:\n{module_logs}")
            return trace or "internal_processor done"

        @self.app.task(name="external_processor_task")
        def task_external_processor(input_dir, case_path, module_bytes, case_uuid):
            """ celery task - external_processor

                The only direct DB write is set_runtime_info (output path + worker name).
                Other status updates done by Celery.
            """
            task_id = current_task.request.id
            worker_name = current_task.request.hostname

            try:
                logger.debug(f"This task is running on worker: {task_id}")
                module_dict = json.loads(module_bytes)
                module_dict['case_path'] = case_path
                module_instance = OsirModule.model_validate(module_dict)

                if module_instance.configuration.processor_os == 'windows' and not OsirAgentConfig().windows_configured:
                    raise RuntimeError(
                        f"Windows module '{module_instance.module_name}' cannot run on this agent: "
                        "Windows machine is not configured. Re-run agent setup and configure a Windows machine."
                    )

                processor = ExternalProcessor(case_path, module_instance, task_id=task_id, agent_name=worker_name)

                logger.debug(f"Check if input of {module_instance.module_name} is in use...")

                with OsirDb() as db:
                    if module_instance.output.type == 'multiple_files':
                        output_path = module_instance.output.output_dir_without_suffix
                    elif module_instance.output.type != 'None':
                        output_path = module_instance.output.output_file_without_suffix
                    else:
                        output_path = "Module without Output"

                    self._is_item_in_use(case_uuid, module_instance, db, exclude_task_id=task_id)
                    db.task.set_runtime_info(task_id, agent=worker_name, output=output_path)

                # Safety net for manually/API file tasks. The normal
                # watchdog path already delays unstable files before task push
                self._wait_for_input_stable(module_instance)

                processor.run_module()
            except Exception as exc:
                with capture_log_output(logger) as log_buffer:
                    logger.error_handler(exc)
                    captured_trace = log_buffer.getvalue()
                _, trace = pop_task_trace(task_id)
                module_logs = "\n".join(trace["logs"]) if trace else captured_trace.strip()
                raise RuntimeError(f"external_processor failed:\n{module_logs}") from exc

            status, trace = pop_task_trace(task_id)
            if status is ProcessingStatus.PROCESSING_FAILED:
                module_logs = "\n".join(trace["logs"]) if trace else "module returned False"
                raise RuntimeError(f"external_processor failed:\n{module_logs}")
            return trace or "external_processor done"

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
        capacity = self._compute_parallel_capacity(
            standalone=self.agent_config.standalone,
            windows_cores=windows_cores
        )
        # Define the arguments for the required workers
        worker_configs = [
            {
                'hostname': f'unix_worker_no_multithread@{host_hostname}',
                'queue': 'unix_no_multithread',
                'autoscale': '1,1'  # Max 1 worker
            },
            {
                'hostname': f'unix_worker_multithread@{host_hostname}',
                'queue': 'unix_multithread',
                # 'autoscale': f'{total_cores},1'  # Max total_cores workers, min 2 workers
                'autoscale': f'{capacity["unix_parallel"]},1'

            },
        ]

        if self.agent_config.windows_configured:
            worker_configs.extend([
                {
                    'hostname': f'windows_worker_no_multithread@{host_hostname}',
                    'queue': 'windows_no_multithread',
                    'autoscale': '1,1'
                },
                {
                    'hostname': f'windows_worker_multithread@{host_hostname}',
                    'queue': 'windows_multithread',
                    'autoscale': f'{capacity["windows_parallel"]},1'
                    # 'autoscale': f'{windows_cores},1'  # Dynamic max workers based on env, min 1 worker
                }
            ])
        else:
            logger.warning("Windows machine not configured — Windows workers will not be started on this agent.")

        if self.agent_config.standalone:
            worker_configs.extend([
                {
                    'hostname': f'unix_worker_no_multithread_disk_only@{host_hostname}',
                    'queue': 'unix_no_multithread_disk_only',
                    'autoscale': '1,1'  # Max 1 worker
                },
                {
                    'hostname': f'unix_worker_multithread_disk_only@{host_hostname}',
                    'queue': 'unix_multithread_disk_only',
                    'autoscale': f'{capacity["unix_disk_parallel"]},1'
                    # 'autoscale': f'{total_cores},2'  # Max total_cores workers, min 2 workers
                }
            ])

        processes = []

        log_dir = OSIR_PATHS.LOG_DIR
        log_file = log_dir / "celery.log"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file.touch(exist_ok=True)

        for config in worker_configs:
            argv = [
                'worker',
                '--loglevel=info',
                f'--hostname={config["hostname"]}',
                '-Q', config['queue'],
                '--time-limit=36000',
                '-E',
                f'--autoscale={config["autoscale"]}',
                f'--logfile={log_file}'
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

import os
import threading
import uuid

from os import environ
from celery import Celery

from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_lib.logger import AppLogger
from osir_service.postgres.OsirDb import OsirDb

logger = AppLogger(__name__).get_logger()


# Process-wide Celery app singleton.
# Single app: the broker connection pool is created once and publishes
# reuse persistent connections/channels

_celery_app = None
_celery_app_lock = threading.Lock()

_windows_configured_cache = None


def _default_result_backend() -> str:
    """Build the PostgreSQL result-backend URL from the same configuration
    sources as OsirDb (POSTGRES_* env vars + agent.yml host resolution)."""
    user = os.getenv('POSTGRES_USER', 'missing POSTGRES_USER env var')
    password = os.getenv('POSTGRES_PASSWORD', 'missing POSTGRES_PASSWORD env var')
    try:
        from osir_lib.core.OsirAgentConfig import OsirAgentConfig
        agent_config = OsirAgentConfig()
        host = "host.docker.internal" if agent_config.standalone else agent_config.master_host
    except FileNotFoundError:
        host = "master-postgres"
    return f"db+postgresql://{user}:{password}@{host}:5432/OSIR_db"


def _get_celery_app() -> Celery:
    global _celery_app
    if _celery_app is None:
        with _celery_app_lock:
            if _celery_app is None:
                rabbitmq_user = os.getenv('RABBITMQ_DEFAULT_USER', 'missing RABBITMQ_DEFAULT_USER env var')
                rabbitmq_password = os.getenv('RABBITMQ_DEFAULT_PASS', 'missing RABBITMQ_DEFAULT_PASS env var')
                broker_url = environ.get(
                    'CELERY_BROKER_URL',
                    f'pyamqp://{rabbitmq_user}:{rabbitmq_password}@master-rabbitmq:5672//'
                )
                result_backend = environ.get('CELERY_RESULT_BACKEND', _default_result_backend())

                app = Celery(name='OSIR', broker=broker_url, backend=result_backend)
                app.conf.update(
                    result_extended=True,
                    task_track_started=True,            # STARTED rows in celery_taskmeta
                    result_expires=None,                # no TTL purge: cleanup is per-case
                    database_short_lived_sessions=True,
                )
                _celery_app = app
    return _celery_app


def _windows_configured() -> bool:
    """Cached check of agent.yml windows configuration (avoids re-parsing
    the YAML config on every task push). Returns True on config errors so
    tasks are dispatched to the queue as before."""
    global _windows_configured_cache
    if _windows_configured_cache is None:
        try:
            from osir_lib.core.OsirAgentConfig import OsirAgentConfig
            _windows_configured_cache = bool(OsirAgentConfig().windows_configured)
        except Exception:
            _windows_configured_cache = True
    return _windows_configured_cache


class TaskService:
    def __init__(self):
        pass

    @staticmethod
    def get_task_name(module: OsirModuleModel):
        if "internal" in module.configuration.processor_type:
            return "internal_processor_task"
        else:
            return "external_processor_task"

    @staticmethod
    def get_queue_name(module: OsirModuleModel):
        if module.configuration.disk_only and module.configuration.no_multithread:
            return f"{module.configuration.processor_os}_no_multithread_disk_only"
        elif module.configuration.disk_only:
            return f"{module.configuration.processor_os}_multithread_disk_only"
        elif module.configuration.no_multithread:
            return f"{module.configuration.processor_os}_no_multithread"
        else:
            return f"{module.configuration.processor_os}_multithread"

    @staticmethod
    def _fail_windows_task(db, case_uuid, handler_uuid, module_name: str, input_match: str) -> str:
        """Create a task row and immediately mark it failed (through the
        Celery result backend) because no Windows machine is configured."""
        custom_task_id = str(uuid.uuid4())
        db.task.create(
            task_id=custom_task_id,
            case_uuid=case_uuid,
            handler_id=handler_uuid,
            agent="Null",
            module=module_name,
            input=input_match
        )
        msg = (
            f"Windows module '{module_name}' cannot run: "
            "Windows machine is not configured on this agent. "
            "Re-run agent setup and configure a Windows machine."
        )
        try:
            # The task is never sent to the broker, so no worker will ever
            # report it: write the FAILURE row in celery_taskmeta ourselves
            # so handler aggregation sees the task as finished+failed.
            _get_celery_app().backend.mark_as_failure(
                custom_task_id, RuntimeError(msg), traceback=msg
            )
        except Exception as e:
            logger.error(f"Could not mark task {custom_task_id} as failed in result backend: {e}")
        logger.warning(
            f"Task '{module_name}' immediately failed: Windows machine not configured."
        )
        return custom_task_id

    @staticmethod
    def push_task(case_path, module_instance: OsirModuleModel, case_uuid, handler_uuid=None):
        """
            Submits a task for asynchronous execution using Celery, specifying the task's parameters and execution queue.

            Args:
                case_path (str): The base directory path where the case files are stored and operations will be performed.
                module_instance (OsirModuleModel): The module instance to be processed in the task.
                case_uuid (str): A unique identifier for the case associated with the task.
                handler_uuid: Handler this task belongs to.

            Environment Variables:
                CELERY_BROKER_URL (str): The URL of the Celery message broker.
                CELERY_RESULT_BACKEND (str): The URL of the backend used to store task results.
        """
        if not module_instance.input.match:
            if module_instance.input.type == "file":
                module_instance.input.match = module_instance.input.file
            else:
                module_instance.input.match = module_instance.input.dir

        # Fail Windows tasks immediately if no Windows machine is configured on this agent
        if module_instance.configuration.processor_os == 'windows' and not _windows_configured():
            with OsirDb() as db:
                return TaskService._fail_windows_task(
                    db, case_uuid, handler_uuid,
                    module_instance.module_name, module_instance.input.match
                )

        app = _get_celery_app()
        custom_task_id = str(uuid.uuid4())

        with OsirDb() as db:
            db.task.create(
                task_id=custom_task_id,
                case_uuid=case_uuid,
                handler_id=handler_uuid,
                agent="Null",
                module=module_instance.module_name,
                input=module_instance.input.match
            )

        app.send_task(
            TaskService.get_task_name(module_instance),
            args=(module_instance.input.match, case_path, module_instance.model_dump_json(), case_uuid),
            task_id=custom_task_id,
            queue=TaskService.get_queue_name(module_instance),
        )

        logger.info(
            f"Task pushed: module={module_instance.module_name} "
            f"task_id={custom_task_id} "
            f"type={module_instance.configuration.processor_type} "
            f"input='{module_instance.input.match}'"
        )

        return custom_task_id

    @staticmethod
    def push_tasks_bulk(case_path, case_uuid, handler_uuid, items: list[dict]) -> list[str]:
        """
            Submits many tasks at once:
              - one bulk INSERT (execute_values) for all task rows,
              - one AMQP producer (single connection/channel) reused for all
                celery publishes.

            Args:
                case_path: normalized case path (same value passed to push_task).
                case_uuid: case UUID.
                handler_uuid: handler UUID.
                items: list of dicts with keys:
                    task_name     -> celery task name
                    queue         -> celery queue name
                    module_name   -> module name
                    match         -> input.match (file path)
                    payload_json  -> serialized OsirModuleModel JSON
                    processor_os  -> module processor_os ('linux'/'windows'/...)

            Returns:
                list[str]: task ids of the dispatched (non-failed) tasks.
        """
        if not items:
            return []

        app = _get_celery_app()

        dispatchable = []
        win_blocked = []

        if any(it.get("processor_os") == "windows" for it in items) and not _windows_configured():
            for it in items:
                (win_blocked if it.get("processor_os") == "windows" else dispatchable).append(it)
        else:
            dispatchable = items

        rows = []
        for it in dispatchable:
            it["task_id"] = str(uuid.uuid4())
            rows.append((
                it["task_id"],
                case_uuid,
                handler_uuid,
                "Null",
                it["module_name"],
                it["match"],
            ))

        with OsirDb() as db:
            if rows:
                db.task.create_bulk(rows)

            for it in win_blocked:
                TaskService._fail_windows_task(
                    db, case_uuid, handler_uuid, it["module_name"], it["match"]
                )

        # Single producer => one connection/channel for the whole batch.
        with app.producer_or_acquire() as producer:
            for it in dispatchable:
                app.send_task(
                    it["task_name"],
                    args=(it["match"], case_path, it["payload_json"], case_uuid),
                    task_id=it["task_id"],
                    queue=it["queue"],
                    producer=producer,
                )
                logger.debug(
                    f"Task pushed (bulk): module={it['module_name']} "
                    f"task_id={it['task_id']} input='{it['match']}'"
                )

        return [it["task_id"] for it in dispatchable]

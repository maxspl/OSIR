import os
from pathlib import Path
import uuid
from threading import Thread, Lock, Event
import logging
from typing import Dict, Optional, List
from uuid import UUID, uuid4
from celery.app.control import Control

from pydantic import BaseModel, ConfigDict, Field

from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_lib.core.OsirUtils import normalize_osir_path
from osir_lib.logger import AppLogger
from osir_lib.logger.logger import CustomLogger, singleton

from osir_service.orchestration.TaskService import TaskService
from osir_service.ipc.OsirIpc import FileManager
from osir_service.postgres.OsirDb import OsirDb
from osir_service.watchdog.WatchdogService import ModuleHandler
from osir_service.orchestration.TaskService import _get_celery_app
logger: CustomLogger = AppLogger(__name__).get_logger()


class HandlerService(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    case_path: str
    modules: List[str]
    module_instances: List[OsirModuleModel]
    case_uuid: UUID
    handler_uuid: UUID
    reprocess_case: bool
    stop_event: Event = Field(default_factory=Event)
    cooldown_period: int = 20

@singleton
class HandlerManager:
    def __init__(self, max_workers: int = 1):
        self.handlers: Dict[UUID, HandlerService] = {}
        self.threads: Dict[UUID, Thread] = {}
        self.lock = Lock()

    def _create_handler(
        self,
        case_path: Path,
        reprocess_case: bool,
        modules: Optional[List[str]] = None,
        module_instances: Optional[list[OsirModuleModel]] = None,
        handler_uuid: Optional[UUID] = None,
    ) -> HandlerService:
        
        if modules is None and module_instances is None:
            raise ValueError("Either modules or module_instances must be provided")

        handler_uuid = handler_uuid or uuid4()

        if not module_instances:
            module_instances = [OsirModuleModel.from_name(module) for module in modules]

        # Always store the canonical module name (the module's `module:` field,
        # which is what osir_tasks.module records). Callers may pass names with a
        # '.yml' extension (e.g. from a profile), while tasks record the bare
        # name; normalizing here keeps the handler's declared modules aligned
        # with the executed ones, so a module can't show up as both "not
        # launched" and "executed" in the UI.
        modules = [module.configuration.module for module in module_instances]

        case_name = os.path.basename(str(case_path))
        with OsirDb() as db:
            case = db.case.get(name=case_name)
            if not case:
                case_uuid = db.case.create(case_name).case_uuid
            else:
                case_uuid = case.case_uuid

        handler = HandlerService(
            case_path=str(case_path),
            modules=modules,
            module_instances=module_instances,
            case_uuid=case_uuid,
            handler_uuid=handler_uuid,
            reprocess_case=reprocess_case,
        )

        with self.lock:
            self.handlers[handler_uuid] = handler

        with OsirDb() as db:
            db.handler.create(
                handler_id=handler.handler_uuid,
                case_uuid=handler.case_uuid,
                modules=handler.modules,
                task_ids=[],
            )

        return handler
        

    def _monitor_directory(
        self,
        handler: HandlerService,
        poll_interval: int,
        reprocess_case: bool,
    ) -> None:
        try:
            module_handler = ModuleHandler(
                Path(handler.case_path),
                handler.cooldown_period,
                handler.module_instances,
                handler.case_uuid,
                handler.handler_uuid,
            )
            module_handler.monitor_directory(handler.case_path, poll_interval, reprocess_case)
        except Exception as e:
            logger.error_handler(e)

    def _start_handler(
        self,
        handler: HandlerService,
        handler_uuid: UUID,
        reprocess_case: bool,
    ) -> None:
        thread = Thread(
            target=self._monitor_directory,
            args=(handler, 10, reprocess_case),
            daemon=True,
        )
        self.threads[handler_uuid] = thread
        thread.start()

    def start(
        self,
        case_path: Optional[Path] = None,
        modules: Optional[List[str]] = None,
        reprocess_case: bool = False,
        handler_service: Optional[HandlerService] = None,
    ) -> tuple[UUID, UUID]:
        if handler_service is None and (case_path is None or modules is None):
            raise ValueError("Either handler_service or both case_path and modules must be provided")

        handler = handler_service or self._create_handler(case_path=case_path, modules=modules, reprocess_case=reprocess_case)

        with self.lock:
            handler_uuid = handler.handler_uuid
            self.handlers[handler_uuid] = handler
            self._start_handler(handler, handler_uuid, handler.reprocess_case)
            logger.debug(f"Handler {handler_uuid} started for case {handler.case_uuid}.")
            return handler_uuid, handler.case_uuid

    def stop(self, handler_uuid: Optional[UUID] = None) -> None:
        with self.lock:
            if handler_uuid:
                self._stop_handler(handler_uuid)
            else:
                logger.debug("No UUID provided to stop handler.")

    def _stop_handler(self, handler_uuid: UUID | str) -> None:
        logger.debug(f"Handler {handler_uuid} will be stopped.")
        uuid_key = handler_uuid if isinstance(handler_uuid, UUID) else UUID(handler_uuid)

        if uuid_key in self.handlers:
            if uuid_key in self.threads:
                self.threads[uuid_key].join(timeout=5)
                del self.threads[uuid_key]

            handler = self.handlers[uuid_key]
            with OsirDb() as db:
                db.handler.update(str(handler.handler_uuid), "processing_done")
            del self.handlers[uuid_key]
            logger.debug(f"Handler {uuid_key} stopped.")

    def run_task(self, module_instance: OsirModuleModel, case_name = None, case_uuid = None, handler_uuid = None):
        """
            Pushes a task to the task queue for processing, without seting up the handler, based on the current module configuration.

            Args:
                module_instance: The module instance to be processed.
        """
        if case_name is None and case_uuid is None:
            raise ValueError("Either case_name or case_uuid must be provided")

        if not case_uuid:
            with OsirDb() as db:
                case = db.case.get(name=case_name)
                if not case:
                    case_uuid = db.case.create(case_name).case_uuid
                else:
                    case_uuid = case.case_uuid

        if handler_uuid:
            handler = self.handlers[handler_uuid]
        else:
            handler = self._create_handler(
                case_path=str(FileManager.get_cases_path(case_name)),
                module_instances=[module_instance],
                reprocess_case=False,
            )

        task_params = (handler.case_path, module_instance, handler.case_uuid, handler.handler_uuid)
        TaskService.push_task(*task_params)

        return handler.handler_uuid
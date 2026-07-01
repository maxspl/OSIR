import os
from pathlib import Path
import uuid
from threading import Thread, Lock, Event
import logging
from typing import Dict, Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_lib.logger import AppLogger
from osir_lib.logger.logger import CustomLogger, singleton

from osir_service.postgres.OsirDb import OsirDb
from osir_service.watchdog.WatchdogService import ModuleHandler

logger: CustomLogger = AppLogger(__name__).get_logger()


class HandlerService(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    case_path: str
    cooldown_period: int
    modules: List[str]
    module_instances: List[OsirModuleModel]
    case_uuid: UUID
    handler_uuid: UUID
    reprocess_case: bool
    stop_event: Event = Field(default_factory=Event)

@singleton
class HandlerManager:
    def __init__(self, max_workers: int = 1):
        self.handlers: Dict[UUID, HandlerService] = {}
        self.threads: Dict[UUID, Thread] = {}
        self.lock = Lock()

    def _create_handler(
        self,
        case_path: Path,
        modules: List[str],
        reprocess_case: bool,
        handler_uuid: Optional[UUID] = None,
    ) -> HandlerService:
        handler_uuid = handler_uuid or uuid4()
        module_instances = [OsirModuleModel.from_name(module) for module in modules]
        cooldown_period = 20  # Cooldown period in seconds

        case_name = os.path.basename(str(case_path))
        with OsirDb() as db:
            case = db.case.get(name=case_name)
            if not case:
                case_uuid = db.case.create(case_name).case_uuid
            else:
                case_uuid = case.case_uuid

        return HandlerService(
            case_path=str(case_path),
            cooldown_period=cooldown_period,
            modules=modules,
            module_instances=module_instances,
            case_uuid=case_uuid,
            handler_uuid=handler_uuid,
            reprocess_case=reprocess_case,
        )

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
        case_path: Path,
        modules: List[str],
        reprocess_case: bool,
    ) -> UUID:
        with self.lock:
            handler = self._create_handler(case_path, modules, reprocess_case)
            handler_uuid = handler.handler_uuid
            self.handlers[handler_uuid] = handler
            self._start_handler(handler, handler_uuid, reprocess_case)
            logger.debug(f"Handler {handler_uuid} started for case {handler.case_uuid}.")
        return handler_uuid, handler.case_uuid

    def stop(self, handler_uuid: Optional[UUID] = None) -> None:
        with self.lock:
            if handler_uuid:
                self._stop_handler(handler_uuid)
            else:
                logger.debug("No UUID provided to stop handler.")

    def _stop_handler(self, handler_uuid: UUID) -> None:
        if handler_uuid in self.handlers:
            self.handlers[handler_uuid].stop_event.set()
            if handler_uuid in self.threads:
                self.threads[handler_uuid].join(timeout=5)
                del self.threads[handler_uuid]
            del self.handlers[handler_uuid]
            logger.debug(f"Handler {handler_uuid} stopped.")

    def shutdown(self) -> None:
        self.stop()
        logger.debug("HandlerManager shutdown complete.")
import time
from typing import TYPE_CHECKING, Optional, Self
from pydantic import BaseModel, PrivateAttr
from osir_lib.logger.logger import CustomLogger
from osir_lib.logger import AppLogger
from osir_api.api.model.OsirApiCaseModel import GetCaseHandlerResponse
from osir_api.api.model.OsirApiHandlerModel import GetHandlerStatusResponse
from osir_service.postgres.model.OsirDbHandlerModel import OsirDbHandlerModel
from osir_client.client.OsirCliDisplay import OsirCliDisplay

logger: CustomLogger = AppLogger().get_logger()

if TYPE_CHECKING:
    from osir_client.client.OsirClient import OsirClient
    from osir_client.client.OsirCliCase import OsirCliCase
    from osir_client.client.OsirCliTask import OsirCliTask


class OsirCliHandler(BaseModel):
    _api: "OsirClient" = PrivateAttr(default=None)
    _context: "OsirCliCase" = PrivateAttr(default=None)

    handler_id: str = None
    _tasks: Optional["OsirCliTask"] = PrivateAttr(default=None)
    _status: Optional[str] = PrivateAttr(default=None)

    @property
    def tasks(self) -> "OsirCliTask":
        if self._tasks is None:
            from osir_client.client.OsirCliTask import OsirCliTask
            self._tasks = OsirCliTask()
            self._tasks._api = self._api
        return self._tasks

    def list(self, case_name: Optional[str] = None) -> Self:
        """
        List all handlers for a given case.
        POST /api/case/{case_name}/handler
        """
        try:
            if not case_name:
                case_name = self._context.name

            response: GetCaseHandlerResponse = self._api.post(
                f"/api/case/{case_name}/handler",
                response_model=GetCaseHandlerResponse
            )

            OsirCliDisplay.handlers(response.response, title=f"Handlers for {case_name}")
            return self

        except Exception as e:
            logger.error(f"Failed to list handlers: {e}")
            return self

    def status(self, wait_end: bool = False, timeout: int = 300, interval: int = 5) -> Self:
        """
        Fetch the handler's current status.
        POST /api/handler/{handler_uuid}/info

        Args:
            wait_end (bool): If True, waits until processing_done or processing_failed.
            timeout (int): Maximum wait time in seconds.
            interval (int): Time between polling requests in seconds.
        """
        start_time = time.time()

        while True:
            response: GetHandlerStatusResponse = self._api.post(
                f"/api/handler/{self.handler_id}/info",
                response_model=GetHandlerStatusResponse
            )
            handler: OsirDbHandlerModel = response.response

            OsirCliDisplay.handlers([handler], title="Handler Status")

            if not wait_end or handler.processing_status in ("processing_done", "processing_failed"):
                self._status = handler.processing_status
                self._tasks = handler.task_id
                return self

            if time.time() - start_time > timeout:
                raise TimeoutError("Timeout: Status did not change within the allowed time.")

            time.sleep(interval)
from typing import TYPE_CHECKING, List, Optional
from pydantic import BaseModel, PrivateAttr

from osir_api.api.model.OsirApiTaskModel import GetTaskInfoResponse, GetTasksListResponse
from osir_api.api.model.OsirApiHandlerModel import GetHandlerStatusResponse

from osir_service.postgres.model.OsirDbTaskModel import OsirDbTaskModel

if TYPE_CHECKING:
    from osir_client.client.OsirClient import OsirClient

from osir_lib.logger import AppLogger
from osir_lib.logger.logger import CustomLogger

from osir_client.client.OsirCliDisplay import OsirCliDisplay

logger: CustomLogger = AppLogger().get_logger()

class OsirCliTask(BaseModel):
    _api: "OsirClient" = PrivateAttr()
    _context: "OsirCliCase" = PrivateAttr()

    @property
    def ctx(self) -> "OsirCliCase":
        return self._context

    def get_task_info(self, task_id: str, print: bool = True) -> "OsirDbTaskModel":
        """
        Retrieve task info by task ID.
        GET /api/tasks/{task_id}/info
        """
        response: GetTaskInfoResponse = self._api.get(f"/api/tasks/{task_id}/info",
        response_model=GetTaskInfoResponse)
        if print:
            OsirCliDisplay.task_info(response.response)
        return response.response

    def list(self, case_name: Optional[str] = None) -> List["OsirDbTaskModel"]:
        """
        List all tasks for a given case.
        POST /api/case/{case_name}/tasks
        """
        try:
            if self.ctx is None or self.ctx.name is None:
                logger.error("You can't run a profile on a not setup case")
                return self

            if not case_name:
                case_name = self._context.name

            response: GetTasksListResponse = self._api.get(
                f"/api/case/{case_name}/tasks",
                response_model=GetTasksListResponse
            )

            OsirCliDisplay.tasks(response.response)
            return self

        except Exception as e:
            logger.error(f"Failed to list handlers: {e}")
            return self

    def _get_handler_task_ids(self, handler_id: str) -> List[str]:
        """
        Helper to retrieve task IDs associated with a given handler.
        POST /api/handler/{handler_uuid}/info
        """
        response: GetHandlerStatusResponse = self._api.post(f"/api/handler/{handler_id}/info",
            response_model=GetHandlerStatusResponse)
        return [str(task_id) for task_id in response.response.task_id]
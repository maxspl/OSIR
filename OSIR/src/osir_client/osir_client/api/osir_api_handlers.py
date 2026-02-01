import time
from typing import TYPE_CHECKING, Optional, Self
from uuid import UUID
from pydantic import BaseModel, PrivateAttr
from tabulate import tabulate
from osir_client.api.osir_api_models import GetHandlerListResponse, GetHandlerStatusResponse
from osir_lib.logger.logger import CustomLogger
from osir_lib.logger import AppLogger

logger: CustomLogger = AppLogger().get_logger()

if TYPE_CHECKING:
    from osir_client.api.osir_api_client import OsirApiClient
    from osir_client.api.osir_api_case import OsirApiCase
    from osir_client.api.osir_api_task import OsirApiTask


class OsirApiHandlers(BaseModel):
    _api: "OsirApiClient" = PrivateAttr(default=None)
    _context: "OsirApiCase" = PrivateAttr(default=None)

    handler_id: str = None
    _tasks: Optional["OsirApiTask"] = None
    _status: Optional[str] = PrivateAttr(default=None)

    def list(self, case_name: Optional[str] = None) -> Self:
        try:
            if not case_name:
                case_name = self._context.case_name
            _response = GetHandlerListResponse(**self._api.post("/api/handler", payload={"case_name": case_name}))

            table_data = []
            for handler in _response.response.handlers:
                row = [
                    handler.case_uuid if handler.case_uuid else "N/A",
                    str(handler.handler_id) if handler.handler_id else "N/A",
                    handler.processing_status if handler.processing_status else "N/A"
                ]
                table_data.append(row)

            title = f"Handler Status Overview Of {case_name}"

            print(f"\n{title}\n{'=' * len(title)}\n")

            headers = ["Case UUID", "Handler ID", "Processing Status"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))

            return self

        except Exception as e:
            logger.error_handler(e)
            return self

    def status(self, wait_end=False, timeout=300, interval=5):
        """
        Fetches the handler's status. If `wait_end=True`, waits for the status to become `expected_status`.

        Args:
            wait_end (bool): If True, waits for the status to change.
            timeout (int): Maximum wait time in seconds.
            interval (int): Time between API requests in seconds.

        Returns:
            dict: The API response.
        """
        start_time = time.time()

        while True:
            _response = GetHandlerStatusResponse(**self._api.post("/api/handler/status", payload={"handler_id": self.handler_id}))
            status = _response.response.processing_status
            handler = _response.response

            table_data = []

            row = [
                handler.case_uuid if handler.case_uuid else "N/A",
                str(handler.handler_id) if handler.handler_id else "N/A",
                handler.processing_status if handler.processing_status else "N/A"
            ]
            table_data.append(row)

            title = f"Handler Status"

            print(f"\n{title}\n{'=' * len(title)}\n")

            headers = ["Case UUID", "Handler ID", "Processing Status"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))

            table_data_details = []
            row_details = [
                ", ".join(handler.modules),
                ", ".join(str(task_id) for task_id in handler.task_ids)
            ]
            table_data_details.append(row_details)

            title_details = "Modules and Task IDs"
            print(f"\n{title_details}\n{'=' * len(title_details)}\n")
            headers_details = ["Modules", "Task IDs"]
            print(tabulate(table_data_details, headers=headers_details, tablefmt="grid"))

            if not wait_end or status == "processing_done" or status == "processing_failed":
                self._status = status
                self.tasks = handler.task_ids
                return self

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout: Status did not change")

            time.sleep(interval)

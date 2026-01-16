from typing import TYPE_CHECKING
from pydantic import BaseModel, PrivateAttr

if TYPE_CHECKING:
    from osir_client.api.osir_api_client import OsirApiClient


class OsirApiLog(BaseModel):
    _api: OsirApiClient = PrivateAttr()

    def get_task_logs(self, task_id: str):
        return self._api.get("/api/logs/task", params={"task_id": task_id})

    def stream(self):
        return self._api.get(f"/api/logs/stream", stream=True)

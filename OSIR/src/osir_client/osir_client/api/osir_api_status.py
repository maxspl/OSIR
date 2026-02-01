from typing import TYPE_CHECKING
from pydantic import BaseModel, PrivateAttr

if TYPE_CHECKING:
    from osir_client.api.osir_api_client import OsirApiClient


class OsirApiStatus(BaseModel):
    _api: "OsirApiClient" = PrivateAttr()

    def get_hanlder_status(self, handler_id):
        return self._api.get("/api/handler/status", params={"handler_id": handler_id})

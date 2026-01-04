from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, PrivateAttr


if TYPE_CHECKING:
    from osir_client.api.osir_api_client import OsirApiClient
    from osir_client.api.osir_api_case import OsirApiCase

class OsirApiHandlers(BaseModel):
    _api : OsirApiClient = PrivateAttr(default=None)
    _context: "OsirApiCase" = PrivateAttr(default=None) 

    def get_hanlder_status(self, handler_id):
        return self._api.get("/api/status/handler", params={"handler_id": handler_id})
from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, PrivateAttr
from osir_lib.logger.logger import AppLogger, CustomLogger
from osir_client.api.osir_api_models import RunModuleResponse
from osir_client.api.osir_api_handlers import OsirApiHandlers
logger: CustomLogger = AppLogger().get_logger()

if TYPE_CHECKING:
    from osir_client.api.osir_api_client import OsirApiClient
    from osir_client.api.osir_api_case import OsirApiCase


class OsirApiModule(BaseModel):
    _api: Optional["OsirApiClient"] = PrivateAttr(default=None)
    _context: Optional["OsirApiCase"] = PrivateAttr(default=None)

    @property
    def ctx(self) -> "OsirApiCase":
        return self._context

    def exists(self, module_path: str):
        return self._api.get(f"/api/module/exists/{module_path}")

    def list_tree(self):
        return self._api.get("/api/module")

    def run(self, module_path: str) -> OsirApiHandlers:
        try:
            _response = RunModuleResponse(**self._api.post(f"/api/module/run", payload={"case_name": self.ctx.case_name, "module_name": module_path}))
            to_return = OsirApiHandlers(handler_id=str(_response.response.handler_id))
            to_return._api = self._api
            return to_return
        except Exception as e:
            logger.error_handler(e)
            return self

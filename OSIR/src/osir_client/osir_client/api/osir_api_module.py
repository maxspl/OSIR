from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, PrivateAttr

if TYPE_CHECKING:
    from osir_client.api.osir_api_client import OsirApiClient
    from osir_client.api.osir_api_case import OsirApiCase

class OsirApiModule(BaseModel):
    _api : Optional["OsirApiClient"] = PrivateAttr(default=None)
    _context: Optional["OsirApiCase"] = PrivateAttr(default=None)

    @property
    def ctx(self) -> "OsirApiCase":
        return self._context

    def exists(self, module_path: str):
        return self._api.get(f"/api/module/exists/{module_path}")
    
    def list_tree(self):
        return self._api.get("/api/module")
    
    def run(self, module_path: str):
        return self._api.get(f"/api/module/run/{module_path}", params={"case_name": self.ctx.case_name})

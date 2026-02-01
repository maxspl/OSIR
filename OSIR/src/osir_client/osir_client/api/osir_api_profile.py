from typing import TYPE_CHECKING
from pydantic import BaseModel, PrivateAttr

if TYPE_CHECKING:
    from osir_client.api.osir_api_client import OsirApiClient
    from osir_client.api.osir_api_case import OsirApiCase


class OsirApiProfile(BaseModel):
    _api: "OsirApiClient" = PrivateAttr()
    _context: "OsirApiCase" = PrivateAttr()

    @property
    def ctx(self) -> "OsirApiCase":
        return self._context

    def exists(self, module_path: str):
        return self._api.get(f"/api/module/exists/{module_path}")

    def list_tree(self):
        return self._api.get("/api/module")

    def run(self, profile_name: str):
        return self._api.get(f"/api/module/run/{profile_name}", params={"case_name": self.ctx.name})

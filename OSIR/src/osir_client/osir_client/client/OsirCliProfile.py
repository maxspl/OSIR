from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, PrivateAttr

from osir_client.client.OsirCliHandler import OsirCliHandler
from osir_client.client.OsirCliDisplay import OsirCliDisplay


from osir_api.api.model.OsirApiProfileModel import GetProfileListResponse, GetProfileInfoResponse, PostProfileRunResponse

from osir_lib.core.model.OsirProfileModel import OsirProfileModel
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

if TYPE_CHECKING:
    from osir_client.client.OsirClient import OsirClient
    from osir_client.client.OsirCliCase import OsirCliCase
    

class OsirCliProfile(BaseModel):
    _api: "OsirClient" = PrivateAttr()
    _context: "OsirCliCase" = PrivateAttr()

    @property
    def ctx(self) -> "OsirCliCase":
        return self._context

    def exists(self, profile_name: str) -> Optional["OsirProfileModel"]:
        """
        Retrieve profile info by name.
        GET /api/profile/{profile_name}/info
        """
        response: GetProfileInfoResponse = self._api.get(f"/api/profile/{profile_name}/info",
                response_model=GetProfileInfoResponse)
        return response.response

    def list(self, print: bool = True) -> list[str]:
        """
        Retrieve all available profiles.
        GET /api/profile
        """
        response: GetProfileListResponse = self._api.get("/api/profile",
                response_model=GetProfileListResponse)

        if print:
            OsirCliDisplay.profiles(response.response)
        return response.response

    def run(self, profile_name: str) -> OsirCliHandler:
        """
        Run a profile against the current case context.
        POST /api/profile/{profile_name}/run
        """
        if self.ctx is None or self.ctx.name is None:
            logger.error("You can't run a profile on a not setup case")
            return self
        try:
            response: PostProfileRunResponse = self._api.post(
                f"/api/profile/{profile_name}/run",
                response_model=PostProfileRunResponse,
                json={"case_name": self.ctx.name}
            )
            handler = OsirCliHandler(handler_id=str(response.response.handler_id))
            handler._api = self._api
            return handler
        except Exception as e:
            logger.error(f"Failed to run profile '{profile_name}': {e}")
            return self
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from pydantic import BaseModel, PrivateAttr

from osir_lib.logger import AppLogger
from osir_client.api.osir_api_response import OsirApiResponse
from osir_client.api.osir_api_client import OsirApiClient
from osir_lib.logger.logger import CustomLogger

logger: CustomLogger = AppLogger(__name__).get_logger()

if TYPE_CHECKING:
    from osir_client.api.osir_api_client import OsirApiClient
    from osir_client.api.osir_api_module import OsirApiModule
    from osir_client.api.osir_api_profile import OsirApiProfile
    from osir_client.api.osir_api_handlers import OsirApiHandlers

class OsirApiCase(BaseModel):
    _api: OsirApiClient = PrivateAttr(default=None)

    case_name: Optional[str] = None
    case_id: Optional[str] = None
    # Move complex/circular objects to PrivateAttrs
    _api: "OsirApiClient" = PrivateAttr()
    _modules: Optional["OsirApiModule"] = PrivateAttr(default=None)
    _profiles: Optional["OsirApiProfile"] = PrivateAttr(default=None)
    _handlers_id: List["OsirApiHandlers"] = PrivateAttr(default_factory=list)

    def __init__(self, api_client, case_name: Optional[str] = None):
        super().__init__(case_name=case_name)
        self._api = api_client

    def model_post_init(self, __context) -> None:
        from osir_client.api.osir_api_module import OsirApiModule
        from osir_client.api.osir_api_profile import OsirApiProfile
        
        self._modules = OsirApiModule(_context=self, _api=self._api)
        self._profiles = OsirApiProfile(context=self, _api=self._api)

    # Use properties so you can still call 'case.modules'
    @property
    def modules(self) -> "OsirApiModule":
        return self._modules

    @property
    def profiles(self) -> "OsirApiProfile":
        return self._profiles

    def get(self, case_name:str):
        try:
            _response = OsirApiResponse(self._api.get("/api/case"))
            if _response and case_name in _response.response['cases']:
                self.name = case_name
                return self
            else:
                logger.error(f"Case {case_name} not found, you can create it with create()")

        except Exception as e:
            logger.error_handler(e)

    def list(self):
        try:
            return OsirApiResponse(self._api.get("/api/case"))
        except Exception as e:
            logger.error_handler(e)
 
    def create(self, case_name: str = None):
        if self.case_name is None and case_name is None:
            raise ValueError("The 'name' parameter is required and cannot be None.")
        try:
            self.case_name = case_name if case_name is not None else self.case_name
            _response = OsirApiResponse(self._api.post("/api/case", self.model_dump())).info()

            return self
        except Exception as e:
            logger.error_handler(e)
        
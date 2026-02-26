from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, PrivateAttr
from tabulate import tabulate

from osir_client.client.OsirCliModule import OsirCliModule
from osir_client.client.OsirCliProfile import OsirCliProfile
from osir_client.client.OsirCliHandler import OsirCliHandler
from osir_client.client.OsirCliTask import OsirCliTask
from osir_client.client.OsirCliDisplay import OsirCliDisplay

from osir_lib.logger.logger import CustomLogger
from osir_lib.logger import AppLogger

from osir_api.api.model.OsirApiCaseModel import GetCaseListResponse, PostCaseCreateResponse

logger: CustomLogger = AppLogger(__name__).get_logger()

if TYPE_CHECKING:
    from osir_client.client.OsirClient import OsirClient


class OsirCliCase(BaseModel):
    """A class to represent and manage an OSIR API case.

    Attributes:
        _api (OsirClient): Private attribute for the OSIR API client.
        name (Optional[str]): The name of the case. Defaults to None.
        case_uuid (Optional[str]): The UUID of the case. Defaults to None.
    """

    _api: "OsirClient" = PrivateAttr()

    name: Optional[str] = None
    case_uuid: Optional[str] = None

    _modules: Optional[OsirCliModule] = PrivateAttr(default=None)
    _profiles: Optional[OsirCliProfile] = PrivateAttr(default=None)
    _handlers: Optional[OsirCliHandler] = PrivateAttr(default=None)
    _tasks: Optional[OsirCliTask] = PrivateAttr(default=None)

    @property
    def modules(self) -> OsirCliModule:
        if self._modules is None:
            self._modules = OsirCliModule()
            self._modules._context = self
            self._modules._api = self._api
        return self._modules

    @property
    def profiles(self) -> OsirCliProfile:
        if self._profiles is None:
            self._profiles = OsirCliProfile()
            self._profiles._context = self
            self._profiles._api = self._api
        return self._profiles

    @property
    def handlers(self) -> OsirCliHandler:
        if self.name is None and self.case_uuid is None:
            logger.error("You can't access handlers on a not setup case")
            return None
        if self._handlers is None:
            self._handlers = OsirCliHandler()
            self._handlers._context = self
            self._handlers._api = self._api
        return self._handlers

    @property
    def tasks(self) -> OsirCliTask:
        if self._tasks is None:
            self._tasks = OsirCliTask()
            self._tasks._api = self._api
            self._tasks._context = self
        return self._tasks

    def get(self, case_name: str, case_uuid: Optional[str] = None) -> OsirCliCase:
        try:
            response = self._api.get("/api/case", response_model=GetCaseListResponse)
            for case in response.response:
                if case.name == case_name or (case_uuid and str(case.case_uuid) == case_uuid):
                    self.name = case.name
                    self.case_uuid = str(case.case_uuid)
                    return self
            logger.error(f"Case '{case_name}' not found. You can create it with create().")
            return self
        except Exception as e:
            logger.error(f"Failed to get case: {e}")
            return self

    def list(self) -> None:
        try:
            response = self._api.get("/api/case", response_model=GetCaseListResponse)
            cases = response.response
            if cases:
                OsirCliDisplay.cases(cases)
            else:
                logger.warning("No case found")
        except Exception as e:
            logger.error(f"Error while getting cases: {e}")

    def create(self, case_name: Optional[str] = None) -> OsirCliCase:
        if self.name is None and case_name is None:
            raise ValueError("The 'case_name' parameter is required and cannot be None.")
        try:
            self.name = case_name if case_name is not None else self.name
            response = self._api.post(f"/api/case/{self.name}", response_model=PostCaseCreateResponse)
            self.case_uuid = str(response.response.case_uuid)
            return self
        except Exception as e:
            logger.error(f"Failed to create case: {e}")
            return self
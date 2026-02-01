from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from pydantic import BaseModel, PrivateAttr
from tabulate import tabulate
from osir_client.api.osir_api_models import GetCaseResponse
from osir_client.api.osir_api_response import OsirApiResponse
from osir_client.api.osir_api_module import OsirApiModule
from osir_client.api.osir_api_profile import OsirApiProfile
from osir_client.api.osir_api_handlers import OsirApiHandlers
from OSIR.src.osir_client.osir_client.api.osir_api_task import OsirApiTask
from osir_lib.logger.logger import CustomLogger
from osir_lib.logger import AppLogger

logger: CustomLogger = AppLogger(__name__).get_logger()

if TYPE_CHECKING:
    from osir_client.api.osir_api_client import OsirApiClient


class OsirApiCase(BaseModel):
    _api: "OsirApiClient" = PrivateAttr()

    case_name: Optional[str] = None
    case_uuid: Optional[str] = None

    _modules: Optional["OsirApiModule"] = None
    _profiles: Optional["OsirApiProfile"] = None
    _handlers: Optional["OsirApiHandlers"] = None

    @property
    def modules(self) -> 'OsirApiModule':
        if self._modules is None and self.case_name is None and self.case_uuid is None:
            logger.error("You can't execute module on not setup case")
        elif self._modules is None and self.case_uuid:
            self._modules = OsirApiModule()
            self._modules._context = self
            self._modules._api = self._api
        return self._modules

    @property
    def profiles(self) -> 'OsirApiProfile':
        if self._profiles is None and self.case_name is None and self.case_uuid is None:
            logger.error("You can't access profiles on a not setup case")
        elif self._profiles is None and (self.case_name or self.case_uuid):
            self._profiles = OsirApiProfile()
            self._profiles._context = self
            self._profiles._api = self._api
        return self._profiles

    @property
    def handlers(self) -> 'OsirApiHandlers':
        if self._handlers is None and self.case_name is None and self.case_uuid is None:
            logger.error("You can't access handlers on a not setup case")
        elif self._handlers is None and (self.case_name or self.case_uuid):
            self._handlers = OsirApiHandlers()
            self._handlers._context = self
            self._handlers._api = self._api
        return self._handlers

    @property
    def log(self) -> 'OsirApiTask':
        if self._log is None and self.case_name is None and self.case_uuid is None:
            logger.error("You can't access logs on a not setup case")
        elif self._log is None and (self.case_name or self.case_uuid):
            self._log = OsirApiTask()
            self._log._api = self._api
        return self._log

    def get(self, case_name: str, case_uuid: Optional[str] = None) -> 'OsirApiCase':
        try:
            _response = GetCaseResponse(**self._api.get("/api/case"))
            if _response and hasattr(_response.response, 'cases'):
                for uuid, name in _response.response.cases:
                    if name == case_name:
                        self.case_name = case_name
                        self.case_uuid = uuid
                        # logger.info(f"Case {self.case_name}-{self.case_uuid} found and setup ! ")
                        return self
                    if case_uuid and case_uuid == uuid:
                        self.case_name = case_name
                        self.case_uuid = uuid
                        # logger.info(f"Case {self.case_name}-{self.case_uuid} found and setup ! ")
                        return self
                logger.error(f"Case '{case_name}' not found. You can create it with create().")
                return self
            else:
                logger.error("No cases found in the response.")
                return self

        except Exception as e:
            logger.error_handler(e)
            return self

    def list(self) -> None:
        try:
            response = GetCaseResponse(**self._api.get("/api/case"))
            cases = response.response.cases

            if cases:
                table = tabulate(cases, headers=["UUID", "NAME"], tablefmt="grid")
                indented_table = "\n".join(" " + line for line in table.splitlines())
                title = f"List of Case Overview"

                print(f"\n{title}\n{'=' * len(title)}\n")
                print(indented_table)
            else:
                logger.warning("No case found")

        except Exception as e:
            logger.error_handler(f"Error while getting cases {e}")

    def create(self, case_name: str = None) -> 'OsirApiCase':
        if self.case_name is None and case_name is None:
            raise ValueError("The 'name' parameter is required and cannot be None.")
        try:
            self.case_name = case_name if case_name is not None else self.case_name
            _response = OsirApiResponse(self._api.post("/api/case", self.model_dump())).info()

            return self
        except Exception as e:
            logger.error_handler(e)

import requests
from typing import TYPE_CHECKING, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, PrivateAttr, field_validator

from osir_client.api.osir_api_case import OsirApiCase
from osir_lib.logger import AppLogger
from osir_client.api.osir_api_response import OsirApiResponse
from osir_lib.logger.logger import CustomLogger

logger: CustomLogger = AppLogger(__name__).get_logger()

CLIENT_VERSION = "1.0"


class OsirApiClient(BaseModel):
    api_url: str
    _cases: Optional[OsirApiCase] = PrivateAttr(default=None)

    @property
    def cases(self) -> OsirApiCase:
        if self._cases is None:
            self._cases = OsirApiCase()
            self._cases._api = self
        return self._cases

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        try:
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error_handler(e)
            raise

    def get(self, endpoint: str, params: Optional[dict] = None) -> Dict[str, Any]:
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, payload: Optional[dict] = None) -> Dict[str, Any]:
        return self._request("POST", endpoint, json=payload)

    def is_active(self) -> bool:
        try:
            return self.get(f"/api/active")
        except:
            return False

    def _check_version(self):
        try:
            raw_response = self.get('api/version')
            api_call = OsirApiResponse(raw_response)

            # Extraction propre des versions
            v_client = CLIENT_VERSION.split('.')
            v_server = [
                str(api_call.response.get('api_major')),
                str(api_call.response.get('api_minor'))
            ]

            if v_server == v_client:
                logger.info('API Client is compatible with FastAPI server')
            else:
                logger.warning(f'Version mismatch: Client {CLIENT_VERSION} / Server {".".join(v_server)}')

        except Exception as e:
            logger.error_handler(e)

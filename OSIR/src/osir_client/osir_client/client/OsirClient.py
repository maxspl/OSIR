
import requests
from typing import Optional, Type, TypeVar
from pydantic import BaseModel, PrivateAttr
from osir_client.client.OsirCliCase import OsirCliCase
from osir_lib.logger import AppLogger
from osir_lib.logger.logger import CustomLogger
from osir_service.ipc.OsirIpcModel import OsirIpcResponse

logger: CustomLogger = AppLogger(__name__).get_logger()

CLIENT_VERSION = "1.0"

T = TypeVar("T", bound=BaseModel)


class OsirClient(BaseModel):
    api_url: str
    _cases: Optional[OsirCliCase] = PrivateAttr(default=None)

    @property
    def cases(self) -> OsirCliCase:
        if self._cases is None:
            self._cases = OsirCliCase()
            self._cases._api = self
        return self._cases

    def _request(self, method: str, endpoint: str, response_model: Type[T], **kwargs) -> T:
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        try:
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
            return response_model(**resp.json())
        except Exception as e:
            logger.error(f"Request failed [{method} {url}]: {e}")
            raise

    def get(self, endpoint: str, response_model: Type[T], params: Optional[dict] = None) -> T:
        return self._request("GET", endpoint, response_model=response_model, params=params)

    def post(self, endpoint: str, response_model: Type[T], json: Optional[dict] = None) -> T:
        return self._request("POST", endpoint, response_model=response_model, json=json)

    def upload(self, endpoint: str, files: dict, data: dict) -> None:
        """
            Multipart file upload.
            POST /api/case/{case_name}/uploads
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        try:
            resp = requests.post(url, files=files, data=data)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"Upload failed [{url}]: {e}")
            raise

    def is_active(self) -> bool:
        """
        Check if the OSIR service is running.
        GET /api/active
        """
        try:
            response = self.get("/api/active", response_model=OsirIpcResponse)
            return response.status == 200
        except Exception:
            return False

    def _check_version(self) -> None:
        """
        Verify client/server version compatibility.
        GET /api/version
        """
        try:
            response = self.get("/api/version", response_model=OsirIpcResponse)
            server_version = str(response.version)

            if server_version == CLIENT_VERSION:
                logger.info("API Client is compatible with FastAPI server")
            else:
                logger.warning(f"Version mismatch: Client {CLIENT_VERSION} / Server {server_version}")
        except Exception as e:
            logger.error(f"Version check failed: {e}")
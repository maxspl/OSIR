import requests
from typing import List, Optional, Dict, Any
from osirlib.logger import AppLogger
from osir_client.api.osir_api_case import OSIRAPICase

logger = AppLogger(__name__).get_logger()
API_VERSION = ""

class OSIRAPIClient:
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip("/")
        self.osir_case = OSIRAPICase()

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        try:
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
            data = resp.json()
            return data
        except Exception as e:
            logger.error_handler(e)
            raise  # Re-raise the exception to handle it in the calling code

    def get(self, endpoint: str, params: Optional[dict] = None) -> Dict[str, Any]:
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, payload: Optional[dict] = None) -> Dict[str, Any]:
        return self._request("POST", endpoint, json=payload)

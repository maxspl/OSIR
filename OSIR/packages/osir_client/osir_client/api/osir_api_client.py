import requests
from typing import List, Optional, Dict, Any
from osirlib.logger import AppLogger
from osir_client.api.osir_api_case import OSIRAPICase
from osir_client.api.osir_api_response import OSIRAPIResponse

logger = AppLogger(__name__).get_logger()

API_VERSION = "1.0"

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

    def _check_version(self):
        try:
            api_call = OSIRAPIResponse(self.get('api/version'))

            if api_call.response['api_major'] == API_VERSION.split('.')[0] and api_call.response['api_minor'] == API_VERSION.split('.')[1]:
                logger.info('API Client is compatible with FastAPI server')
            else:
                logger.warning('API Client is not compatible with FastAPI server')

        except Exception as e:
            logger.error_handler(e)
        
        
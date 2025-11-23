from typing import Optional
from pydantic import BaseModel, PrivateAttr

from osirlib.logger import AppLogger

from osir_client.api.osir_api_response import OSIRAPIResponse

logger = AppLogger(__name__).get_logger()

class OSIRAPICase(BaseModel):
    name: Optional[str] = None
    _client = PrivateAttr()

    def __init__(self, name: Optional[str] = None, client=None):
        super().__init__(name=name)
        self._client = client

    def create(self, name: Optional[str] = None):
        if name is None:
            raise ValueError("The 'name' parameter is required and cannot be None.")
                
        if self._client is None:
            logger.error("Client is not initialized. Cannot proceed with the request.")
            return  
        
        self.name = name

        try:
            _response = OSIRAPIResponse(self._client.get("/api/version"))
        except Exception as e:
            logger.error_handler(e)

        return self

    def list(self):
        if not self.name:
            raise ValueError("The 'name' parameter is required and cannot be None.")

        try:
            _response = OSIRAPIResponse(self._client.get("/api/case"))
            
        except Exception as e:
            logger.error_handler(e)
 
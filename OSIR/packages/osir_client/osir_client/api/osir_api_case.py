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
            return 
        
        if self._client is None:
            return 
         
        self.name = name
        _response = OSIRAPIResponse(self._client.get("/api/version"))

        return self

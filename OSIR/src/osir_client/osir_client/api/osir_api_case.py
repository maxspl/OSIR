from typing import Optional
from pydantic import BaseModel, PrivateAttr

from osirlib.logger import AppLogger

from osir_client.api.osir_api_response import OSIRAPIResponse

logger = AppLogger(__name__).get_logger()

class OSIRAPICase(BaseModel):
    name: Optional[str] = None
    _client = PrivateAttr()

    def __init__(self, client, name: Optional[str] = None):
        super().__init__(name=name)
        self._client = client

    def list(self):
        try:
            return OSIRAPIResponse(self._client.get("/api/case"))
        except Exception as e:
            logger.error_handler(e)
 
    def create(self, name: str = None):
        if self.name is None and name is None:
            raise ValueError("The 'name' parameter is required and cannot be None.")
        try:
            self.name = name if name is not None else self.name
            _response = OSIRAPIResponse(self._client.post("/api/case", self.model_dump())).info()

            return self
        except Exception as e:
            logger.error_handler(e)
        
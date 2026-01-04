from pydantic import BaseModel
from typing import Dict, Any
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

class OsirApiResponse(BaseModel):
    version: str
    status: int
    response: Dict[str, Any]

    def __init__(self, response: Dict[str, Any]):
        try:
            version = response['version']
            status = response['status']
            response_data = response['response']
        except KeyError as e:
            logger.error(f"Missing required field: {e}")
            raise ValueError(f"Missing required field: {e}")

        super().__init__(version=version, status=status, response=response_data)

    def info(self):
        logger.info(self.model_dump())
                
        
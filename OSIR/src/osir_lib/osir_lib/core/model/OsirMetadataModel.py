from typing import Optional
from pydantic import BaseModel
from osir_lib.core.model.LiteralModel import OS_TYPE
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()


class OsirMetadataModel(BaseModel):
    """
        Data model defining the structure and validation for OSIR Metadata of modules.
    """
    version: str
    author: str
    description: str
    os: Optional[OS_TYPE] = None
    
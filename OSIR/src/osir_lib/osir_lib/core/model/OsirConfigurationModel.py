from typing import Optional

from pydantic import BaseModel
from osir_lib.core.model.LiteralModel import MODULE_TYPE, PROCESSOR_OS, PROCESSOR_TYPE
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()


class OsirConfigurationModel(BaseModel):
    """
        Data model defining the structure and validation for OSIR modules configuration.
    """
    module: str
    type: MODULE_TYPE
    disk_only: bool
    no_multithread: bool
    processor_type: list[PROCESSOR_TYPE]
    processor_os: PROCESSOR_OS
    alt_module: Optional[str] = None
    
from typing import Optional
from pydantic import BaseModel

from osir_lib.core.model.OsirProfileModel import OsirProfileModel

class OsirIpcModel(BaseModel):
    action: str
    case_path: str = None
    modules: Optional[list[str]] = None
    profile: Optional[OsirProfileModel] = None

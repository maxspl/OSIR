from typing import Optional
from pydantic import BaseModel

class OsirToolModel(BaseModel):
    path: str
    cmd: str
    source: Optional[str] = None
    version: Optional[str] = None
    license: Optional[str] = None
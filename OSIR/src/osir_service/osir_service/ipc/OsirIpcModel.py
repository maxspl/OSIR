from typing import Optional
from pydantic import BaseModel

class OsirIpcModel(BaseModel):
    action: str
    case_name: Optional[str] = None
    modules: Optional[list[str]] = None
    profile: Optional[str] = None
    task_id: Optional[str] = None
    case_uuid: Optional[str] = None
    handler_id: Optional[str] = None

class OsirIpcResponse(BaseModel):
    version: float
    status: Optional[int] = 200
    message: Optional[str] = None
    response: Optional[dict] = {}
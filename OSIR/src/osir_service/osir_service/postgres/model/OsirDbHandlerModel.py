from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime

class OsirDbHandlerModel(BaseModel):
    handler_id: UUID
    case_uuid: UUID
    modules: List[str]
    task_id: List[UUID]
    processing_status: str
    created_at: Optional[datetime] = None

    # JOIN WITH OsirDbCaseModel 

    case_name: Optional[str] = None
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime

class OsirDbHandlerModel(BaseModel):
    handler_id: UUID
    case_uuid: UUID
    modules: List[str]
    task_id: Optional[List[UUID]] = []
    # Number of tasks linked to this handler (computed in SQL). Replaces
    # shipping the full task_id list, which does not scale on large cases.
    task_count: Optional[int] = 0
    processing_status: str
    created_at: Optional[datetime] = None

    # JOIN WITH OsirDbCaseModel 

    case_name: Optional[str] = None
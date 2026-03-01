from pydantic import BaseModel
from uuid import UUID

class OsirDbCaseModel(BaseModel):
    case_uuid: UUID
    name: str
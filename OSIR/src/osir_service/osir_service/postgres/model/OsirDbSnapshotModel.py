from pydantic import BaseModel

class OsirDbSnapshotModel(BaseModel):
    case_uuid: str
    case_path: str
    path: str
    entry_type: str
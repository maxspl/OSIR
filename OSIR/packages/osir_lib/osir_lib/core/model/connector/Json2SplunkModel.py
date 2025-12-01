from typing import Optional
from pydantic import BaseModel

class Json2SplunkConfigModel(BaseModel):
    source: str
    sourcetype: str
    # CHANGE TO BLOB MATCH OR JUST OUTPUT OF THE MODULE
    name_rex: str # change to rex
    path_suffix: str
    host_rex: str # change to rex
    timestamp_path: Optional[list[str]] # Optional ? 
    timestamp_format: str # Existe Timestamp format class ? 
    artifact: str

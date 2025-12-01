from typing import Optional
from pydantic import BaseModel


class OsirOutputModel(BaseModel):
    type: Optional[str] = None
    format:  Optional[str] = None
    output_dir: Optional[str] = None
    output_file: Optional[str] = None
    output_prefix: Optional[str] = None
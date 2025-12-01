from typing import Optional
from pydantic import BaseModel

from osir_lib.core.model.LiteralModel import INPUT_TYPE

class OsirInputModel(BaseModel):
    type: INPUT_TYPE
    # Change to blob search
    name: Optional[str] = None
    path: Optional[str] = None
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

from osir_lib.core.model.LiteralModel import INPUT_TYPE

class OsirInputModel(BaseModel):
    type: INPUT_TYPE

    #OLD 
    file: Optional[str] = None
    dir: Optional[str] = None
    path: Optional[str] = None
    name: Optional[str] = None

    # NEW 
    paths: Optional[list[str]] = None
    _match: Optional[Path] = None
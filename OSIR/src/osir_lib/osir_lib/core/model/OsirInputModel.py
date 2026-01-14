from pathlib import Path
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from osir_lib.core.model.LiteralModel import INPUT_TYPE

class OsirInputModel(BaseModel):
    type: INPUT_TYPE

    #OLD 
    path: Optional[str] = None
    name: Optional[str] = None

    file: Optional[str] = None
    dir: Optional[str] = None
    
    # NEW 
    paths: Optional[list[str]] = None
    match: Optional[Path] = None

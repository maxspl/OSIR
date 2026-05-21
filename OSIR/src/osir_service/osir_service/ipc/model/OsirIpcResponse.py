from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from osir_lib.core.OsirConstants import OSIR

class OsirIpcResponse(BaseModel):
    """
        Standardized response envelope returned by the OSIR Master service.

        Attributes:
            version (float): The current version of the OSIR framework for compatibility checks.
            status (int): The HTTP-style status code (e.g., 200 for success, 400+ for errors).
            message (str, optional): A descriptive summary of the operation result.
            response (dict, optional): A container for the actual data payload (e.g., log traces, 
                handler IDs, or case metadata).
    """
    version: float = OSIR.VERSION
    status: Optional[int] = 200
    message: Optional[str] = None
    response: Optional[Union[Dict[str, Any], List[Any]]] = {}
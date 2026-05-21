from typing import Optional
from pydantic import BaseModel


class OsirIpcRequest(BaseModel):
    """
    Standard data model for IPC requests within the OSIR service.
    
    Attributes:
        action (str): The command to execute (e.g., 'exec_module', 'create_case', 'get_task_log').
        params (dict, optional): Dictionary containing all parameters for the action.
    """
    action: str
    params: Optional[dict] = None

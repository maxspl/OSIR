from typing import Optional
from pydantic import BaseModel


class OsirIpcModel(BaseModel):
    """
        Standard data model for outgoing Inter-Process Communication (IPC) requests.

        Attributes:
            action (str): The command to execute (e.g., 'exec_module', 'create_case', 'get_task_log').
            case_name (str, optional): The human-readable name of the forensic case.
            modules (list[str], optional): A list of module names to execute.
            profile (str, optional): The name of a pre-defined forensic profile to run.
            task_id (str, optional): The unique UUID of a specific Celery task for log retrieval.
            case_uuid (str, optional): The database UUID associated with a case.
            handler_id (str, optional): The unique identifier for a case execution monitor.
    """
    action: str
    case_name: Optional[str] = None
    modules: Optional[list[str]] = None
    profile: Optional[str] = None
    task_id: Optional[str] = None
    case_uuid: Optional[str] = None
    handler_id: Optional[str] = None


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
    version: float
    status: Optional[int] = 200
    message: Optional[str] = None
    response: Optional[dict] = {}

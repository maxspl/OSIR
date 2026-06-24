from typing import Any, Dict, List, Optional, Union
from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse
from osir_service.postgres.model.OsirDbTaskModel import OsirDbTaskModel
from pydantic import BaseModel

""" 
==========================================
API Endpoint: GET /task/{task_id}/restart
==========================================
Description: Restart a task

Request model:
  - PARAMS: task_id

Response model:
  - GetRestartTask

==========================================
"""


class GetRestartTaskResponse(OsirIpcResponse):
    response: dict

""" 
==========================================
API Endpoint: GET /task/{task_id}/info
==========================================
Description: Get task info from OSIR DB

Request model:
  - PARAMS: task_id

Response model:
  - GetTaskInfoResponse

==========================================
"""


class GetTaskInfoResponse(OsirIpcResponse):
    response: OsirDbTaskModel


""" 
==========================================
API Endpoint: GET /task
==========================================
Description: Get all task from OSIR DB

Request model:
  - PARAMS: task_id

Response model:
  - GetTaskInfoResponse

==========================================
"""


class PaginatedTaskResponse(BaseModel):
    """Pagination metadata and task data."""
    tasks: List[OsirDbTaskModel]
    total: int
    page: int
    page_size: int
    total_pages: int


class GetTasksListResponse(OsirIpcResponse):
    response: PaginatedTaskResponse


""" 
==========================================
API Endpoints: POST /handler/{handler_id}/stats
               GET  /case/{case_name}/stats
==========================================
Description: Aggregated task statistics (counts per status, per module,
throughput) computed in SQL on the celery-joined effective statuses.

Response model:
  - GetTaskStatsResponse

==========================================
"""


class GetTaskStatsResponse(OsirIpcResponse):
    response: Dict[str, Any]

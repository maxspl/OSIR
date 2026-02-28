from typing import List
from osir_service.ipc.OsirIpcModel import OsirIpcResponse
from osir_service.postgres.model.OsirDbTaskModel import OsirDbTaskModel

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


class GetTasksListResponse(OsirIpcResponse):
    response: List[OsirDbTaskModel]

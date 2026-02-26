
from typing import List
from osir_service.postgres.model.OsirDbCaseModel import OsirDbCaseModel
from osir_service.ipc.OsirIpcModel import OsirIpcResponse
from osir_service.postgres.model.OsirDbHandlerModel import OsirDbHandlerModel

from pydantic import BaseModel


""" 
==========================================
API Endpoint: GET /api/case
==========================================
Description: Retrieves all of the OSIR cases.

Request model:
  - N/A

Response model:
  - GetCaseListResponse

==========================================
"""

class GetCaseListResponse(OsirIpcResponse):
    response: List[OsirDbCaseModel]


""" 
==========================================
API Endpoint: POST /api/case/{case_name}
==========================================
Description: Create an OSIR case.

Request model:
  - PARAMS: case_name

Response model:
  - PostCaseCreateResponse

==========================================
"""
class PostCaseCreateResponse(OsirIpcResponse):
  response: OsirDbCaseModel

""" 
==========================================
API Endpoint: GET /api/case/{case_name}/handler
==========================================
Description: Retrieves all handler of an OSIR cases.

Request model:
  - PARAMS: case_name

Response model:
  - GetHandlerResponse

==========================================
"""
class GetCaseHandlerResponse(OsirIpcResponse):
    response: List[OsirDbHandlerModel]
from typing import List, Union
from osir_service.ipc.OsirIpcModel import OsirIpcResponse
from osir_service.postgres.model.OsirDbHandlerModel import OsirDbHandlerModel
from osir_lib.core.model.OsirProfileModel import OsirProfileModel

from pydantic import BaseModel

""" 
==========================================
API Endpoint: GET /api/profile
==========================================
Description: Retrieves all of the OSIR profile.

Request model:
  - N/A

Response model:
  - GetProfileListResponse

==========================================
"""


class GetProfileListResponse(OsirIpcResponse):
    response: List[str]


""" 
==========================================
API Endpoint: GET /api/module/{module_name}/info
==========================================
Description: Return the OSIR module info if it exists.

Request model:
  - PARAMS: module_name

Response model:
  - GetProfileInfoResponse

==========================================
"""


class GetProfileInfoResponse(OsirIpcResponse):
    response: Union[OsirProfileModel, None]


""" 
==========================================
API Endpoint: POST /api/profile/{module_name}/run
==========================================
Description: Run a OSIR profile on a case

Request model:
  - PARAMS: module_name

Response model:
  - OsirDbHandlerModel

==========================================
"""


class PostProfileRunRequest(BaseModel):
    case_name: str


class PostProfileRunResponse(OsirIpcResponse):
    response: OsirDbHandlerModel

from typing import List, Optional
from osir_service.postgres.model.OsirDbHandlerModel import OsirDbHandlerModel
from osir_service.postgres.model.OsirDbTaskModel import OsirDbTaskModel

from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from pydantic import BaseModel

""" 
==========================================
API Endpoint: GET /api/handler/{handler_id}/info
==========================================
Description: Retrieves status of an OSIR Handler.

Request model:
  - PARAMS: handler_uuid

Response model:
  - GetHandlerStatusResponse

==========================================
"""


class GetHandlerStatusResponse(OsirIpcResponse):
    response: OsirDbHandlerModel

""" 
==========================================
API Endpoint: POST /api/handler/create
==========================================
Description: Create a new OSIR Handler.

Request model:
  - PostHandlerCreateRequest

Response model:
  - PostHandlerCreateResponse

==========================================
"""


class PostHandlerCreateRequest(BaseModel):
    profile: Optional[str] = None
    profile_module_to_add: Optional[list[str]] = None
    profile_module_to_remove: Optional[list[str]] = None
    modules: Optional[list[str]] = None
    case_name: str
    reprocess: bool = False
    modified_modules: Optional[list[OsirModuleModel]] = None


class PostHandlerCreateResponse(OsirIpcResponse):
    response: OsirDbHandlerModel

class PostHandlerAdvancedCreateRequest(BaseModel):
    files_modules: Optional[str] = None
    files_input: Optional[list[str]] = None
    folders_modules: Optional[str] = None
    files_in_folder_modules: Optional[str] = None
    folders_input: Optional[list[str]] = None
    endpoint_name: Optional[str] = None
    case_name: Optional[str] = None


class PostHandlerDeleteRequest(BaseModel):
    handler_uuid: str

class PostHandlerDeleteResponse(OsirIpcResponse):
    response: OsirDbHandlerModel




class GetHandlerTaskLogsResponse(OsirIpcResponse):
    response: List[OsirDbTaskModel]
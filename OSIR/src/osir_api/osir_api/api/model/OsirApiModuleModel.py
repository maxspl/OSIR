from __future__ import annotations

from typing import Optional, Union
from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_service.postgres.model.OsirDbHandlerModel import OsirDbHandlerModel
from osir_service.postgres.model.OsirDbTaskModel import OsirDbTaskModel
from pydantic import BaseModel

""" 
==========================================
API Endpoint: GET /api/module
==========================================
Description: Retrieves all of the OSIR module.

Request model:
  - N/A

Response model:
  - GetModuleListResponse

==========================================
"""


class GetModuleListResponse(OsirIpcResponse):
    response: list[str]

""" 
==========================================
API Endpoint: POST /api/module/info
==========================================
Description: Return the OSIR module info if it exists.

Request model:
  - PostModuleInfoRequest

Response model:
  - GetModuleExistsResponse

==========================================
"""


class PostModuleInfoRequest(BaseModel):
    modules: list[str]
    keys: list[str] = ["all"]


class GetModuleExistsResponse(OsirIpcResponse):
    response: Union[None, dict[str, dict]]

""" 
==========================================
API Endpoint: POST /api/module/run
==========================================
Description: Run a OSIR module on a case

Request model:
  - PostModuleRunRequest

Response model:
  - PostModuleRunResponse

==========================================
"""


class PostModuleRunRequest(BaseModel):
    module_name: str
    case_name: str
    input_path: Optional[str] = None


class PostModuleRunResponse(OsirIpcResponse):
    response: OsirDbHandlerModel

""" 
==========================================
API Endpoint: POST /api/module/run_on_file
==========================================
Description: Run a OSIR module on a case

Request model:
  - PostModuleRunRequest

Response model:
  - PostModuleRunOnFileResponse

==========================================
"""


class PostModuleRunOnFileResponse(OsirIpcResponse):
    response: OsirDbTaskModel

from __future__ import annotations

from typing import Optional, Union
from osir_service.ipc.OsirIpcModel import OsirIpcResponse
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


class OsirModuleLiveResponseModel(BaseModel):
    """Represents a live_response subgroup (windows or unix)."""
    modules: list[str] = []
    packages: Optional[OsirModuleSubGroupModel] = None
    storage: Optional[OsirModuleSubGroupModel] = None
    process: Optional[OsirModuleSubGroupModel] = None
    network: Optional[OsirModuleSubGroupModel] = None
    hardware: Optional[OsirModuleSubGroupModel] = None
    system: Optional[OsirModuleSubGroupModel] = None


class OsirModuleSubGroupModel(BaseModel):
    """Represents a simple subgroup with only a list of modules (no further nesting)."""
    modules: list[str] = []


class OsirModuleOsGroupModel(BaseModel):
    """Represents an OS-specific group (windows or unix) with dissect and live_response."""
    modules: list[str] = []
    live_response: Optional[OsirModuleLiveResponseModel] = None
    dissect: Optional[OsirModuleSubGroupModel] = None


class OsirModuleTreeModel(BaseModel):
    """Represents the full module tree returned by GET /api/module."""
    modules: list[str] = []
    windows: Optional[OsirModuleOsGroupModel] = None
    unix: Optional[OsirModuleOsGroupModel] = None
    splunk: Optional[OsirModuleSubGroupModel] = None
    scan: Optional[OsirModuleSubGroupModel] = None
    network: Optional[OsirModuleSubGroupModel] = None
    pre_process: Optional[OsirModuleSubGroupModel] = None
    test: Optional[OsirModuleSubGroupModel] = None


class GetModuleListResponse(OsirIpcResponse):
    response: OsirModuleTreeModel


""" 
==========================================
API Endpoint: GET /api/module/{module_name}/info
==========================================
Description: Return the OSIR module info if it exists.

Request model:
  - N/A

Response model:
  - GetModuleExistsResponse

==========================================
"""


class GetModuleExistsResponse(OsirIpcResponse):
    response: Union[None, OsirModuleModel]


""" 
==========================================
API Endpoint: POST /api/module/{module_name}/run
==========================================
Description: Run a OSIR module on a case

Request model:
  - PostModuleRunRequest

Response model:
  - PostModuleRunResponse

==========================================
"""


class PostModuleRunRequest(BaseModel):
    case_name: str
    input_path: Optional[str] = None


class PostModuleRunResponse(OsirIpcResponse):
    response: OsirDbHandlerModel


""" 
==========================================
API Endpoint: POST /api/module/{module_name}/run_on_file
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
from __future__ import annotations

from typing import Union
from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse
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

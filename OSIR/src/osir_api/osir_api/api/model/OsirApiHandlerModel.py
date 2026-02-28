from osir_service.postgres.model.OsirDbHandlerModel import OsirDbHandlerModel
from osir_service.ipc.OsirIpcModel import OsirIpcResponse

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

from typing import Generator, Optional

from osir_service.ipc.OsirSocket import OsirSocket
from osir_service.ipc.model.OsirIpcRequest import OsirIpcRequest
from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse
from osir_api.api.OsirApiExceptions import UnexpectedException
from osir_api.api.OsirApiResponse import handle_response
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

def OsirIpcCall(action: str, params: Optional[dict] = {}, response_only: bool = False) -> OsirIpcResponse:
    """
    Sends an IPC request and returns the validated response.
    Raises UnexpectedException on any error.
    """
    try:
        with OsirSocket() as client:
            request = OsirIpcRequest(action=action, params=params)
            response = OsirIpcResponse.model_validate_json(client.send(request))
            return handle_response(response, response_only)
    except Exception as e:
        logger.error_handler(e)
        raise UnexpectedException(str(e))

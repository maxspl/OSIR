from typing import Generator, Optional, Union
from fastapi.responses import JSONResponse

from osir_service.ipc.OsirSocket import OsirSocket
from osir_service.ipc.model.OsirIpcRequest import OsirIpcRequest
from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse
from osir_api.api.OsirApiExceptions import UnexpectedException
from osir_api.api.OsirApiResponse import handle_response
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

def OsirIpcCall(action: str, params: Optional[dict] = {}, response_only: bool = False) -> Union[JSONResponse, dict]:
    """
    Sends an IPC request and returns the validated response.
    Raises UnexpectedException on any error.
    If response contains headers, they are automatically applied to the HTTP response.
    """
    try:
        with OsirSocket() as client:
            request = OsirIpcRequest(action=action, params=params)
            response = OsirIpcResponse.model_validate_json(client.send(request))
            result = handle_response(response, response_only)
            
            # If result contains headers, create a JSONResponse with them
            if isinstance(result, dict) and "headers" in result:
                headers = result.pop("headers")
                return JSONResponse(content=result, headers=headers)
            
            return result
    except Exception as e:
        logger.error_handler(e)
        raise UnexpectedException(str(e))

from fastapi import HTTPException

from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse

from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

def handle_response(response: OsirIpcResponse, response_only: bool = False):
    if not response.message:
        response.message = "Everything is working as it should!"

    if not (200 <= response.status < 300):
        response.message = "Oups... Something went wrong!"
        raise HTTPException(
            status_code=response.status,
            detail=response.response.get("error", "Unknown error")
        )
    
    if response_only:
        return response.response

    result = response.model_dump()
    if isinstance(response.response, dict) and "headers" in response.response:
        result["headers"] = response.response["headers"]
    
    return result

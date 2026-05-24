from fastapi import HTTPException

from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse

from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

def handle_response(response: OsirIpcResponse, response_only: bool = False):
    if not response.message:
        response.message = "Everything is working as it should!"

    if response.status != 200:
        response.message = "Oups... Something went wrong !"
        raise HTTPException(
            status_code=response.status,
            detail=response.response["error"]
        )
    
    if response_only:
        return response.response

    return response.model_dump()

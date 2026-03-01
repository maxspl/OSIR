from fastapi import HTTPException

from osir_service.ipc.OsirIpcModel import OsirIpcResponse


def handle_response(response: OsirIpcResponse):
    if not response.message:
        response.message = "Everything is working as it should!"

    if response.status != 200:
        response.message = "Oups... Something went wrong !"
        raise HTTPException(
            status_code=response.status,
            detail=response.response["error"]
        )
    return response.model_dump()

from fastapi import APIRouter

from osir_api.api.OsirApiExceptions import UnexpectedExceptionResponse
from osir_api.api.OsirIpcCall import OsirIpcCall

from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse

router = APIRouter()


@router.get("/active",
            response_model=OsirIpcResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def osir_is_active():
    return OsirIpcCall("socket_on") 

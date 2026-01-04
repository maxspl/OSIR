from fastapi import APIRouter
from osir_api.api.response import handle_response
from osir_api.api.exceptions import UnexpectedException, UnexpectedExceptionResponse

from osir_service.ipc.OsirIpcModel import OsirIpcModel, OsirIpcResponse
from osir_service.ipc.OsirIpcClient import OsirIpcClient

router = APIRouter()

API_VERSION = "1.0"

@router.get("/active",
    response_model=OsirIpcResponse,
    responses={500: {"model": UnexpectedExceptionResponse}})
def osir_is_active():
    try:
        client = OsirIpcClient()
        action = OsirIpcModel(action="socket_on")
        response = OsirIpcResponse.model_validate_json(client.send(action))
        return handle_response(response)
    except Exception as e:
        raise UnexpectedException(str(e))
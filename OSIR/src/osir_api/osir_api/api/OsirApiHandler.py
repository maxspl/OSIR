from fastapi import APIRouter

from osir_service.ipc.OsirIpcClient import OsirIpcClient
from osir_service.ipc.OsirIpcModel import OsirIpcModel, OsirIpcResponse

from osir_api.api.model.OsirApiHandlerModel import GetHandlerStatusResponse
from osir_api.api.OsirApiExceptions import UnexpectedException, UnexpectedExceptionResponse
from osir_api.api.OsirApiResponse import handle_response

router = APIRouter()

@router.post("/handler/{handler_id}/info",
             response_model=GetHandlerStatusResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def status_handler(handler_id: str):
    try:
        client = OsirIpcClient()
        action = OsirIpcModel(action="get_handler_status", handler_id=handler_id)
        response = OsirIpcResponse.model_validate_json(client.send(action))
        return handle_response(response)
    except Exception as e:
        raise UnexpectedException(str(e))


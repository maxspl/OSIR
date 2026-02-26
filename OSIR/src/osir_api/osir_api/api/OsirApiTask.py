
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from osir_service.ipc.OsirIpcClient import OsirIpcClient
from osir_service.ipc.OsirIpcModel import OsirIpcModel, OsirIpcResponse
from osir_api.api.model.OsirApiTaskModel import GetTaskInfoResponse
from osir_api.api.OsirApiExceptions import UnexpectedException, UnexpectedExceptionResponse
from osir_api.api.OsirApiResponse import handle_response

router = APIRouter()

@router.get("/tasks/{task_id}/info",
            response_model=GetTaskInfoResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def logs_task(task_id: str):
    try:
        client = OsirIpcClient()
        action = OsirIpcModel(action="get_task_log", task_id=task_id)
        response = OsirIpcResponse.model_validate_json(client.send(action))
        return handle_response(response)
    except Exception as e:
        raise UnexpectedException(str(e))


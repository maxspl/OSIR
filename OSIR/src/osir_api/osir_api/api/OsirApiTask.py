
from fastapi import APIRouter

from osir_api.api.model.OsirApiTaskModel import GetTaskInfoResponse
from osir_api.api.OsirApiExceptions import UnexpectedExceptionResponse
from osir_api.api.OsirIpcCall import OsirIpcCall

router = APIRouter()

@router.get("/tasks/{task_id}/info",
            response_model=GetTaskInfoResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def logs_task(task_id: str):
    return OsirIpcCall("get_task_log", params={"task_id": task_id}) 

@router.get("/tasks/{task_id}/restart",
            response_model=GetTaskInfoResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def logs_task(task_id: str):
    return OsirIpcCall("restart_task", params={"task_id": task_id}) 
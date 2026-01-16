import datetime
import time
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from osir_service.ipc.OsirIpcClient import OsirIpcClient
from osir_service.ipc.OsirIpcModel import OsirIpcModel, OsirIpcResponse
from osir_api.api.exceptions import UnexpectedException, UnexpectedExceptionResponse
from osir_api.api.response import handle_response

router = APIRouter()


def log_generator(log_file_path: str):
    with open(log_file_path, "r") as f:
        # Go to the end of the file first
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)  # Wait for new logs
                continue
            yield f"data: {line}\n\n"


@router.get("/logs/stream",
            response_model=OsirIpcResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
async def stream_logs():
    log_path = "/OSIR/OSIR/src/osir_lib/log/OSIR.log"
    return StreamingResponse(log_generator(log_path), media_type="text/event-stream")


# ==========================================
# API_CALL : Get Task Log
# ==========================================

class TaskLogResponseCore(BaseModel):
    task_id: str
    timestamp: Optional[str] = None
    function: Optional[str] = None
    duration_seconds: Optional[float] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    logs: Optional[List[str]] = None


class TaskLogResponse(OsirIpcResponse):
    response: TaskLogResponseCore


@router.get("/logs/task",
            response_model=OsirIpcResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def logs_task(task_id: str):
    try:
        client = OsirIpcClient()
        action = OsirIpcModel(action="get_task_log", task_id=task_id)
        response = OsirIpcResponse.model_validate_json(client.send(action))
        return handle_response(response)
    except Exception as e:
        raise UnexpectedException(str(e))

import time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from osir_service.ipc.OsirIpcClient import OsirIpcClient
from osir_service.ipc.OsirIpcModel import OsirIpcModel, OsirIpcResponse
from osir_api.api.exceptions import UnexpectedException, UnexpectedExceptionResponse
from osir_api.api.response import handle_response

router = APIRouter()

# ==========================================
# API_CALL : Get Handler Status
# ==========================================

class GetHandlerStatusRequest(BaseModel):
    handler_id: UUID

class GetHandlerStatusResponseCore(BaseModel):
    handler_id: UUID
    # TODO: Replace with UUID after rework
    case_uuid: str
    modules: list[str]
    task_ids: list[UUID]
    processing_status: str

class GetHandlerStatusResponse(OsirIpcResponse):
    response: GetHandlerStatusResponseCore
    
@router.post("/handler/status", 
    response_model=GetHandlerStatusResponse,
    responses={500: {"model": UnexpectedExceptionResponse}})
def status_handler(handler: GetHandlerStatusRequest):
    try:
        client = OsirIpcClient()
        action = OsirIpcModel(action="get_handler_status", handler_id=str(handler.handler_id))
        response = OsirIpcResponse.model_validate_json(client.send(action))
        return handle_response(response)
    except Exception as e:
        raise UnexpectedException(str(e))

# ==========================================
# API_CALL : Get Case Handler
# ==========================================

class GetCaseHandlerRequest(BaseModel):
    case_name: str

class GetHandlerStatusResponseCore(BaseModel):
    handler_id: Optional[UUID]
    # TODO: Replace with UUID after rework
    case_uuid: Optional[str]
    modules: Optional[list[str]]
    task_ids: Optional[list[UUID]]
    processing_status: Optional[str]

class GetHandlerStatusResponse(OsirIpcResponse):
    response: GetHandlerStatusResponseCore

@router.post("/handler", 
    response_model=GetHandlerStatusResponse,
    responses={500: {"model": UnexpectedExceptionResponse}})
def retrieved_case_handler(request: GetCaseHandlerRequest):
    try:
        client = OsirIpcClient()
        action = OsirIpcModel(action="get_case_handler", case_name=request.case_name)
        response = OsirIpcResponse.model_validate_json(client.send(action))
        return handle_response(response)
    except Exception as e:
        raise UnexpectedException(str(e))
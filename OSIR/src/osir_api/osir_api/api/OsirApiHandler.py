from fastapi import APIRouter

from osir_api.api.model.OsirApiHandlerModel import GetHandlerTaskLogsResponse, PostHandlerAdvancedCreateRequest, GetHandlerStatusResponse, PostHandlerCreateRequest, PostHandlerCreateResponse, PostHandlerDeleteRequest, PostHandlerDeleteResponse
from osir_api.api.OsirApiExceptions import UnexpectedExceptionResponse

from osir_api.api.OsirIpcCall import OsirIpcCall

router = APIRouter()


@router.post("/handler/create",
             response_model=PostHandlerCreateResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def create_handler(request: PostHandlerCreateRequest):
    return OsirIpcCall("create_handler", 
            params={
                "profile": request.profile,
                "modules": request.modules,
                "case_name": request.case_name,
                "reprocess": request.reprocess,
                "modified_modules": request.modified_modules
            })

@router.post("/handler/advanced",
             response_model=PostHandlerCreateResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def create_handler_advanced(request: PostHandlerAdvancedCreateRequest):
    return OsirIpcCall("create_advanced_handler", 
            params={
                "files_modules": request.files_modules,
                "files_input": request.files_input,
                "folders_modules": request.folders_modules,
                "folders_input": request.folders_input,
                "endpoint_name": request.endpoint_name,
                "files_in_folder_modules": request.files_in_folder_modules,
                "case_name": request.case_name,
            })

@router.post("/handler/{handler_id}/info",
             response_model=GetHandlerStatusResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def status_handler(handler_id: str):
    return OsirIpcCall("get_handler_status", params={"handler_id": handler_id})

@router.post("/handler/{handler_id}/task_info",
             response_model=GetHandlerTaskLogsResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def status_handler(handler_id: str):
    return OsirIpcCall("get_handler_task_info", params={"handler_id": handler_id})

@router.post("/handler/delete",
             response_model=PostHandlerDeleteResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def create_handler(request: PostHandlerDeleteRequest):
    return OsirIpcCall("delete_handler", 
            params={
                "handler_uuid": request.handler_uuid,
            })


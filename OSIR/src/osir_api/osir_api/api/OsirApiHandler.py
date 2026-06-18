from fastapi import APIRouter
from typing import Optional

from osir_api.api.model.OsirApiTaskModel import GetTaskStatsResponse, PaginatedTaskResponse, GetTasksListResponse
from osir_api.api.model.OsirApiHandlerModel import GetHandlerTaskLogsResponse, PostHandlerAdvancedCreateRequest, GetHandlerStatusResponse, PostHandlerCreateRequest, PostHandlerCreateResponse, PostHandlerDeleteRequest, PostHandlerDeleteResponse
from osir_api.api.OsirApiExceptions import UnexpectedExceptionResponse

from osir_api.api.OsirIpcCall import OsirIpcCall
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()
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

@router.post("/handler/{handler_id}/stats",
             response_model=GetTaskStatsResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def stats_handler(handler_id: str):
    return OsirIpcCall("get_task_stats", params={"handler_id": handler_id})

@router.post("/handler/{handler_id}/task_info",
             response_model=GetHandlerTaskLogsResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def status_handler(handler_id: str):
    return OsirIpcCall("get_handler_task_info", params={"handler_id": handler_id})

@router.get("/handler/{handler_id}/tasks",
            response_model=GetTasksListResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def get_handler_tasks(
    handler_id: str,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    module: Optional[str] = None
):
    """
    Get paginated tasks for a specific handler.
    
    Args:
        handler_id: The handler UUID
        page: Page number (default: 1)
        page_size: Number of items per page (default: 20)
        status: Filter by processing status (optional)
        module: Filter by module name (optional)
    """
    params: dict = {"handler_id": handler_id, "page": page, "page_size": page_size}
    if status:
        params["processing_status"] = status
    if module:
        params["module"] = module
    return OsirIpcCall("get_tasks", params=params)

@router.post("/handler/delete",
             response_model=PostHandlerDeleteResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def create_handler(request: PostHandlerDeleteRequest):
    return OsirIpcCall("delete_handler", 
            params={
                "handler_uuid": request.handler_uuid,
            })


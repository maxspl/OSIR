import os
from fastapi import APIRouter

from osir_api.api.OsirApiExceptions import UnexpectedException, UnexpectedExceptionResponse
from osir_api.api.OsirApiResponse import handle_response
from osir_api.api.model.OsirApiModuleModel import GetModuleListResponse, GetModuleExistsResponse, PostModuleRunRequest, PostModuleInfoRequest, PostModuleRunResponse, PostModuleRunOnFileResponse
from osir_api.api.OsirIpcCall import OsirIpcCall

from osir_lib.core.FileManager import FileManager

router = APIRouter()


@router.get("/module",
            response_model=GetModuleListResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def get_modules():
    return OsirIpcCall("get_modules")


@router.post("/module/info",
            response_model=GetModuleExistsResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def module_info(request: PostModuleInfoRequest):
    return OsirIpcCall("get_module_info", params={"modules": request.modules, "keys": request.keys})


@router.post("/module/run",
             response_model=PostModuleRunResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def run_module(request: PostModuleRunRequest):
    case_path = FileManager.get_cases_path(request.case_name)
    return OsirIpcCall("exec_module", params={"modules": [request.module_name], "case_path": str(case_path)})


@router.post("/module/run_on_file",
             response_model=PostModuleRunOnFileResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def run_module_on_file(request: PostModuleRunRequest):
    case_path = FileManager.get_cases_path(request.case_name)
    return OsirIpcCall("exec_module", 
            params={"modules": [request.module_name],
                   "case_path": str(case_path),
                   "input_path": request.input_path})

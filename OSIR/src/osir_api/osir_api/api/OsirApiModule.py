from fastapi import APIRouter

from osir_api.api.OsirApiExceptions import UnexpectedExceptionResponse
from osir_api.api.model.OsirApiModuleModel import GetModuleListResponse, GetModuleExistsResponse, PostModuleInfoRequest
from osir_api.api.OsirIpcCall import OsirIpcCall

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

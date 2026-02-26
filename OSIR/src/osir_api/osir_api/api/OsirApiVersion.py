
from fastapi import APIRouter
from osir_service.ipc.OsirIpcModel import OsirIpcResponse
from osir_api.api.OsirApiMetadata import API_VERSION
from osir_api.api.OsirApiExceptions import UnexpectedExceptionResponse

router = APIRouter()


@router.get("/version",
            response_model=OsirIpcResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def get_version():
    return {
        "version": API_VERSION,
        "status": 200,
        "response": {
            "api_major": API_VERSION.split('.')[0],
            "api_minor": API_VERSION.split('.')[1]
        }
    }

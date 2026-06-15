from pydantic import BaseModel
from fastapi import Request
from fastapi.responses import JSONResponse

from osir_api.api.OsirApiMetadata import API_VERSION
from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse

UNEXPECTED_ERROR = "API - UNEXPECTED ERROR: {error}"
HTTP_ERROR = "API - HTTP ERROR: {error}"


class UnexpectedExceptionResponseCore(BaseModel):
    error: str


class UnexpectedExceptionResponse(OsirIpcResponse):
    response: UnexpectedExceptionResponseCore


class UnexpectedException(Exception):
    def __init__(self, error: str):
        self.error = error


class HTTPExceptionResponseCore(BaseModel):
    error: str


class HTTPExceptionResponse(OsirIpcResponse):
    response: HTTPExceptionResponseCore


class HTTPExceptionCustom(Exception):
    def __init__(self, status_code: int, error: str):
        self.status_code = status_code
        self.error = error


async def unexpected_error_handler(request: Request, exc: UnexpectedException):
    return JSONResponse(
        status_code=500,
        content={
            "version": API_VERSION,
            "status": 500,
            "response": {
                "error": UNEXPECTED_ERROR.format(error=exc.error)
            }
        }
    )


async def http_error_handler(request: Request, exc: HTTPExceptionCustom):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "version": API_VERSION,
            "status": exc.status_code,
            "response": {
                "error": HTTP_ERROR.format(error=exc.error)
            }
        }
    )

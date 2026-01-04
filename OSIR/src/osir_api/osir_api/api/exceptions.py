from pydantic import BaseModel
from fastapi import Request
from fastapi.responses import JSONResponse

from osir_api.api.metadata import API_VERSION
from osir_service.ipc.OsirIpcModel import OsirIpcResponse

UNEXPECTED_ERROR = "UNEXPECTED ERROR: {error}"

class UnexpectedExceptionResponseCore(BaseModel):
    error: str

class UnexpectedExceptionResponse(OsirIpcResponse):
    response: UnexpectedExceptionResponseCore

class UnexpectedException(Exception):
    def __init__(self, error: str):
        self.error = error

async def unexpected_error_handler(request: Request, exc: UnexpectedException):
    return JSONResponse(
        status_code=500,
        content= {
        "version": API_VERSION,
        "status": 500,
        "response": {
            "error": UNEXPECTED_ERROR.format(error=exc.error)
        }
        }
    )
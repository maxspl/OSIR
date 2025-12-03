from osir_api.api.response import ERROR_RESPONSE
from fastapi import Request
from fastapi.responses import JSONResponse

# Centralized error messages
MODULE_NOT_FOUND = "MODULE YAML FILE NOT FOUND: {module}"
MODULE_VALIDATION_ERROR = "MODULE YAML VALIDATION ERROR: {error}"
MODULE_LOAD_ERROR = "ERROR LOADING MODULE YAML: {error}"
UNEXPECTED_ERROR = "UNEXPECTED ERROR: {error}"

# Custom exception classes
class ModuleNotFoundException(Exception):
    def __init__(self, module: str):
        self.module = module

class ModuleValidationException(Exception):
    def __init__(self, error: str):
        self.error = error

class ModuleLoadException(Exception):
    def __init__(self, error: str):
        self.error = error

class UnexpectedException(Exception):
    def __init__(self, error: str):
        self.error = error


# Exception handlers
async def module_not_found_handler(request: Request, exc: ModuleNotFoundException):
    return JSONResponse(
        status_code=422,
        content=ERROR_RESPONSE(422, MODULE_NOT_FOUND.format(module=exc.module))
    )

async def module_validation_handler(request: Request, exc: ModuleValidationException):
    return JSONResponse(
        status_code=422,
        content=ERROR_RESPONSE(422, MODULE_VALIDATION_ERROR.format(error=exc.error))
    )

async def module_load_handler(request: Request, exc: ModuleLoadException):
    return JSONResponse(
        status_code=400,
        content=ERROR_RESPONSE(400, MODULE_LOAD_ERROR.format(error=exc.error))
    )

async def unexpected_error_handler(request: Request, exc: UnexpectedException):
    return JSONResponse(
        status_code=500,
        content=ERROR_RESPONSE(422, UNEXPECTED_ERROR.format(error=exc.error))
    )

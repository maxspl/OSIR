from uuid import UUID
from pydantic import BaseModel
from fastapi import APIRouter

from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_service.ipc.OsirIpcClient import OsirIpcClient
from osir_service.ipc.OsirIpcModel import OsirIpcModel, OsirIpcResponse
from osir_api.api.exceptions import UnexpectedException, UnexpectedExceptionResponse
from osir_api.api.response import handle_response
from osir_api.api.version import API_VERSION

router = APIRouter()

# ==========================================
# API CALL : Get Case
# ==========================================

class GetCaseResponseCore(BaseModel):
    cases: list[str]

class GetCaseResponse(OsirIpcResponse):
    response: GetCaseResponseCore

@router.get("/case", 
    response_model=GetCaseResponse,
    responses={500: {"model": UnexpectedExceptionResponse}})
def get_case():
    try:
        response = OsirIpcResponse(
            version=API_VERSION,
            response={
                "cases" : FileManager.get_cases(OSIR_PATHS.CASES_DIR)
            }
        )
        return handle_response(response)
    
    except Exception as e:
        raise UnexpectedException(str(e))

# ==========================================
# API_CALL : Create Case
# ==========================================

class CaseCreateRequest(BaseModel):
    case_name: str

class CreateCaseResponseCore(BaseModel):
    case_name: str
    case_uuid: UUID
    case_path: str
    state: str

class CreateCaseResponse(OsirIpcResponse):
    response: CreateCaseResponseCore

@router.post("/case", 
    response_model=CreateCaseResponse,
    responses={500: {"model": UnexpectedExceptionResponse}})
def create_case(request: CaseCreateRequest):
    try:
        client = OsirIpcClient()
        action = OsirIpcModel(action="create_case", case_name=request.case_name)
        response = OsirIpcResponse.model_validate_json(client.send(action))
        return handle_response(response)
    except Exception as e:
        raise UnexpectedException(str(e))

    
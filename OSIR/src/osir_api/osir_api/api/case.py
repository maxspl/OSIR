from pydantic import BaseModel
from fastapi import APIRouter

from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirConstants import OSIR_PATHS

from osir_api.api.version import API_VERSION

router = APIRouter()

# Define a Pydantic model for the expected request body
class CaseCreateRequest(BaseModel):
    name: str

    
@router.get("/case")
def get_case():
    return {
        "version": API_VERSION,
        "status": 200,
        "response": {
            "cases" : FileManager.get_cases(OSIR_PATHS.CASES_DIR)
        }
    }

@router.post("/case")
def create_case(request: CaseCreateRequest):

    case_name = request.name

    state, case_path = FileManager.create_case(OSIR_PATHS.CASES_DIR, case_name=case_name)
    return {
        "version": API_VERSION,
        "status": 200,
        "response": {
            "message": f'Case {state} in {case_path}'  
        }
    }
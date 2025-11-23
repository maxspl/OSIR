from pydantic import BaseModel
from fastapi import APIRouter

from osirlib.core.FileManager import FileManager
from osirlib.core import StaticVars

router = APIRouter()

API_VERSION = "1.0"

# Define a Pydantic model for the expected request body
class CaseCreateRequest(BaseModel):
    name: str

    
@router.get("/case")
def get_case():
    return {
        "version": API_VERSION,
        "status": 200,
        "response": {
            "cases" : FileManager.get_cases(StaticVars.CASES_DIR)
        }
    }

@router.post("/case")
def create_case(request: CaseCreateRequest):

    case_name = request.name

    
    return {
        "version": API_VERSION,
        "status": 200,
        "response": {
            "message": 'Case created in ' + FileManager.create_case(StaticVars.CASES_DIR, case_name=case_name)
        }
    }
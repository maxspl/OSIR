from fastapi import APIRouter

from osirlib.core.FileManager import FileManager
from osirlib.core import StaticVars
router = APIRouter()

API_VERSION = "1.0"

@router.get("/case")
def get_case():
    return {
        "version": API_VERSION,
        "status": 200,
        "response": {
            "cases" : FileManager.get_cases(StaticVars.CASES_DIR)
        }
    }

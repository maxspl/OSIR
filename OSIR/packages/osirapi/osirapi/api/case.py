from fastapi import APIRouter

from osirlib.osirlib.core.FileManager import FileManager
from osirlib.osirlib.core.
router = APIRouter()

API_VERSION = "1.0"

@router.get("/case")
def get_case():
    FileManager.get_cases()

    return {
        "version": API_VERSION,
        "status": 200,
        "response": {
            "api_major": API_VERSION.split('.')[0],
            "api_minor": API_VERSION.split('.')[1]
        }
    }

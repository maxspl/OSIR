from fastapi import APIRouter

router = APIRouter()

API_VERSION = "1.0"

@router.get("/version")
def get_version():
    return {
        "version": API_VERSION,
        "status": 200,
        "response": {
            "api_major": API_VERSION.split('.')[0],
            "api_minor": API_VERSION.split('.')[1]
        }
    }

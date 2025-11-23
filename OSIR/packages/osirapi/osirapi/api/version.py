from fastapi import APIRouter

router = APIRouter()

@router.get("/version")
def get_version():
    return {"message": "OSIR API v1.0"}

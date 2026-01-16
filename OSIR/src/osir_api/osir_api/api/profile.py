from uuid import UUID
from pydantic import BaseModel
from fastapi import APIRouter

from osir_api.api.version import API_VERSION
from osir_api.api.response import handle_response
from osir_api.api.exceptions import UnexpectedException, UnexpectedExceptionResponse

from osir_lib.logger.logger import CustomLogger
from osir_service.ipc.OsirIpcModel import OsirIpcResponse

from osir_lib.core.model.OsirProfileModel import OsirProfileModel
from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.logger import AppLogger

logger: CustomLogger = AppLogger(__name__).get_logger()

router = APIRouter()


# ==========================================
# API_CALL : Get Profile
# ==========================================

class GetProfileResponseCore(BaseModel):
    profiles: list[str]


class GetProfileResponse(OsirIpcResponse):
    response: GetProfileResponseCore


@router.get("/profile",
            response_model=GetProfileResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def get_profiles():
    try:
        profiles_dir = OSIR_PATHS.PROFILES_DIR
        if not profiles_dir.exists():
            raise Exception(f"Profiles directory not found: {profiles_dir}")

        profiles = []
        for profile_file in profiles_dir.glob("*.yml"):
            profiles.append(profile_file.name)

        response = OsirIpcResponse(
            version=API_VERSION,
            status=200,
            response={"profiles": profiles}
        )
        return handle_response(response)
    except Exception as e:
        raise UnexpectedException(str(e))

# ==========================================
# API_CALL : Profile Exists
# ==========================================


class GetProfileExistsResponseCore(BaseModel):
    exists: bool
    profile: OsirProfileModel


class GetProfileExistsResponse(OsirIpcResponse):
    response: GetProfileExistsResponseCore


@router.get("/profile/exists/{profile_name}",
            response_model=GetProfileExistsResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def profile_exists(profile_name: str):
    try:
        profile_path = FileManager.get_profile_path(profile_name, raise_error=False)

        response = OsirIpcResponse(
            version=API_VERSION,
            status=200,
        )

        if profile_path:
            profile_data = OsirProfileModel.from_yaml(str(profile_path))
            response.response = {"exists": True, "profile": profile_data}
        else:
            response.response = {"exists": False, "profile": None}

        return handle_response(response)
    except Exception as e:
        raise UnexpectedException(str(e))

# ==========================================
# API_CALL : Run Profile
# ==========================================


class RunProfileRequest(BaseModel):
    profile_name: str
    case_name: str


class RunProfileResponseCore(BaseModel):
    handler_id: UUID


class RunProfileResponse(OsirIpcResponse):
    response: RunProfileResponseCore


@router.post("/profile/run",
             response_model=OsirIpcResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def run_profile(request: RunProfileRequest):
    try:
        from osir_service.ipc.OsirIpcModel import OsirIpcModel
        from osir_service.ipc.OsirIpcClient import OsirIpcClient

        profile_path = FileManager.get_profile_path(request.profile_name)
        if not profile_path.exists():
            raise UnexpectedException(request.profile_name)

        client = OsirIpcClient()
        action = OsirIpcModel(action="exec_profile", profile=request.profile_name, case_name=request.case_name)

        response = OsirIpcResponse.model_validate_json(client.send(action))
        return handle_response(response)

    except Exception as e:
        logger.error_handler(e)
        raise UnexpectedException(str(e))

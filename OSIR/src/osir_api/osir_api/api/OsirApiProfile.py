from fastapi import APIRouter

from osir_api.api.OsirApiMetadata import API_VERSION
from osir_api.api.OsirApiResponse import handle_response
from osir_api.api.OsirApiExceptions import UnexpectedException, UnexpectedExceptionResponse
from osir_api.api.model.OsirApiProfileModel import GetProfileListResponse, GetProfileInfoResponse, PostProfileRunResponse, PostProfileRunRequest
from osir_lib.logger.logger import CustomLogger
from osir_service.ipc.OsirIpcModel import OsirIpcResponse

from osir_lib.core.model.OsirProfileModel import OsirProfileModel
from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.logger import AppLogger

logger: CustomLogger = AppLogger(__name__).get_logger()

router = APIRouter()


@router.get("/profile",
            response_model=GetProfileListResponse,
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
            response=profiles
        )
        return handle_response(response)
    except Exception as e:
        raise UnexpectedException(str(e))


@router.get("/profile/{profile_name}/info",
            response_model=GetProfileInfoResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def profile_exists(profile_name: str):
    try:
        profile_path = FileManager.get_profile_path(profile_name, raise_error=False)

        response = OsirIpcResponse(
            version=API_VERSION,
            status=200,
        )

        if profile_path:
            response.message = "Profile info retrieved."
            response.response = OsirProfileModel.from_yaml(str(profile_path))
        else:
            response.message = "Profile not found."
            response.response = None

        return handle_response(response)
    except Exception as e:
        raise UnexpectedException(str(e))


@router.post("/profile/{profile_name}/run",
             response_model=PostProfileRunResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def run_profile(request: PostProfileRunRequest, profile_name: str):
    try:
        from osir_service.ipc.OsirIpcModel import OsirIpcModel
        from osir_service.ipc.OsirIpcClient import OsirIpcClient

        profile_path = FileManager.get_profile_path(profile_name)
        if not profile_path.exists():
            raise UnexpectedException(profile_name)

        client = OsirIpcClient()
        action = OsirIpcModel(action="exec_profile", profile=profile_name, case_name=request.case_name)

        response = OsirIpcResponse.model_validate_json(client.send(action))
        return handle_response(response)

    except Exception as e:
        logger.error_handler(e)
        raise UnexpectedException(str(e))

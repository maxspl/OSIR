import os
from collections import defaultdict

from fastapi import APIRouter

from osir_service.ipc.OsirIpcModel import OsirIpcModel, OsirIpcResponse
from osir_service.ipc.OsirIpcClient import OsirIpcClient

from osir_api.api.OsirApiExceptions import UnexpectedException, UnexpectedExceptionResponse
from osir_api.api.OsirApiResponse import handle_response
from osir_api.api.OsirApiMetadata import API_VERSION
from osir_api.api.model.OsirApiModuleModel import GetModuleListResponse, GetModuleExistsResponse, PostModuleRunRequest, PostModuleRunResponse, PostModuleRunOnFileResponse

from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()
router = APIRouter()


def module_instance(module_path: str):
    # GLOB PATTERN ?
    yaml_files = FileManager.get_yaml_files(OSIR_PATHS.MODULES_DIR)
    modules = FileManager.resolve_modules_parent_dir(yaml_files)

    if module_path.endswith('.yml'):
        module_path = module_path.replace('.yml', '')

    module_path = module_path.replace('.', '/')
    module_path = module_path + '.yml'

    for module in modules:
        if module == module_path or os.path.basename(module) == module_path:
            try:
                return OsirModuleModel.from_yaml(FileManager.get_module_path(module))  # ou le vrai chemin
            except Exception as e:
                raise e


def make_node():
    """Returns a normalized node structure."""
    return defaultdict(make_node, {"modules": []})


@router.get("/module",
            response_model=GetModuleListResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def get_modules():
    try:
        yaml_files = FileManager.get_yaml_files(OSIR_PATHS.MODULES_DIR)
        modules = FileManager.resolve_modules_parent_dir(yaml_files)

        structured_modules = make_node()

        for module_path in modules:
            parts = module_path.split('/')
            path_parts = parts[:-1]
            module_name = os.path.basename(module_path)

            if not path_parts:
                structured_modules["other"]["modules"].append(module_name)
                continue

            current = structured_modules
            for i, part in enumerate(path_parts):
                current = current[part]

            current["modules"].append(module_name)

        def convert(d):
            """Convert nested defaultdicts to dicts recursively."""
            if not isinstance(d, defaultdict) and not isinstance(d, dict):
                return d
            return {k: convert(v) for k, v in d.items()}

        response = OsirIpcResponse(
            version=API_VERSION,
            status=200,
            response=convert(structured_modules)
        )
        return handle_response(response)

    except Exception as e:
        raise UnexpectedException(str(e))


@router.get("/module/{module_name}/info",
            response_model=GetModuleExistsResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def module_exists(module_name: str):

    try:
        module_model: OsirModuleModel = module_instance(module_path=module_name)

        response = OsirIpcResponse(
            version=API_VERSION,
            status=200,
        )
       
        if module_model:
            response.message = "Module Info Retrieved."
            response.response = module_model.model_dump()
        else:
            response.message = "Module not found."
            response.response = None

        return handle_response(response)
    except Exception as e:
        raise UnexpectedException(str(e))


@router.post("/module/{module_name}/run",
             response_model=PostModuleRunResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def run_module(request: PostModuleRunRequest, module_name: str):
    try:
        client = OsirIpcClient()
        action = OsirIpcModel(
            action="exec_module", 
            modules=[module_name],
            case_name=request.case_name)
        response = OsirIpcResponse.model_validate_json(client.send(action))
        return handle_response(response)
    except Exception as e:
        raise UnexpectedException(str(e))


@router.post("/module/{module_name}/run/file",
             response_model=PostModuleRunOnFileResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def run_module(request: PostModuleRunRequest, module_name: str):        # noqa: F811
    try:
        client = OsirIpcClient()
        action = OsirIpcModel(
            action="exec_module", 
            modules=[module_name],
            case_name=request.case_name,
            input_path=request.input_path)
        response = OsirIpcResponse.model_validate_json(client.send(action))
        return handle_response(response)
    except Exception as e:
        raise UnexpectedException(str(e))

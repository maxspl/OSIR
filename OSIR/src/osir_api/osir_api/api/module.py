import os
from collections import defaultdict

from pydantic import ValidationError
from fastapi import APIRouter

from osir_lib.core.FileManager import FileManager
from osir_lib.core import StaticVars
from osir_api.api.version import API_VERSION
from osir_lib.core.model.OsirModuleModel import OsirModuleModel

from osir_api.api.exceptions import (
    ModuleNotFoundException,
    ModuleValidationException,
    ModuleLoadException,
    UnexpectedException
)

from osir_service.orchestration.TaskService import TaskService

router = APIRouter()

def module_instance(module_path: str):
    # GLOB PATTERN ? 
    yaml_files = FileManager.get_yaml_files(StaticVars.MODULES_DIR)
    modules = FileManager.resolve_modules_parent_dir(yaml_files)

    sanitize_module = module_path.replace('.','/').replace('\\','/')

    if sanitize_module.endswith('/yml'):
        sanitize_module = sanitize_module.replace('/yml','.yml')

    if not sanitize_module.endswith('.yml'):
        sanitize_module = sanitize_module + '.yml'
    for module in modules:
        if module.endswith(sanitize_module):
            try:
                return OsirModuleModel.from_yaml(FileManager.full_path_module(module))  # ou le vrai chemin
            except FileNotFoundError:
                raise ModuleNotFoundException(sanitize_module)
            except ValidationError as e:
                raise ModuleValidationException(str(e))
            except ValueError as e:
                raise ModuleLoadException(str(e))
            except Exception as e:
                raise UnexpectedException(str(e))
    
    raise ModuleNotFoundException(sanitize_module)
 
def make_node():
    """Returns a normalized node structure."""
    return defaultdict(make_node, {"modules": []})


@router.get("/module")
def get_modules():
    yaml_files = FileManager.get_yaml_files(StaticVars.MODULES_DIR)
    modules = FileManager.resolve_modules_parent_dir(yaml_files)

    structured_modules = make_node()

    for module_path in modules:
        parts = module_path.split('/')
        path_parts = parts[:-1]  # directories
        module_name = os.path.basename(module_path)

        # no directory → goes to "autre"
        if not path_parts:
            structured_modules["other"]["modules"].append(module_name)
            continue

        current = structured_modules
        for i, part in enumerate(path_parts):
            current = current[part]  # move down in the node

        # add module only at final directory level
        current["modules"].append(module_name)

    def convert(d):
        """Convert nested defaultdicts to dicts recursively."""
        if not isinstance(d, defaultdict) and not isinstance(d, dict):
            return d
        return {k: convert(v) for k, v in d.items()}

    response = {
        "version": API_VERSION,
        "status": 200,
        "response": {
            "modules": convert(structured_modules)
        }
    }

    return response

@router.get("/module/exists/{module_path}")
def module_exists(module_path: str):   
    return {
        "version": API_VERSION,
        "status": 200,
        "response": module_instance(module_path=module_path).model_dump()
    }

@router.get("/module/run/{module_path}")
def run_module(module_path: str):
    TaskService.run_task("test", module_instance(module_path=module_path), "internal_processor_task", queue=None, case_uuid='tot')
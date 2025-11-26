import os
from collections import defaultdict
from fastapi import APIRouter

from osir_lib.core.FileManager import FileManager
from osir_lib.core.BaseModule import BaseModule
from osir_lib.core import StaticVars
from osir_api.api.version import API_VERSION

router = APIRouter()


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
    exists = False

    yaml_files = FileManager.get_yaml_files(StaticVars.MODULES_DIR)
    modules = FileManager.resolve_modules_parent_dir(yaml_files)

    sanitize_module = module_path.replace('.','/').replace('\\','/')

    if sanitize_module.endswith('/yml'):
        sanitize_module = sanitize_module.replace('/yml','.yml')

    if not sanitize_module.endswith('.yml'):
        sanitize_module = sanitize_module + '.yml'
    
    for module in modules:
        if module.endswith(sanitize_module):
            exists = True
            module_info = BaseModule(sanitize_module.split('/')[-1])
            break

    if not exists:
        return {
            "version": API_VERSION,
            "status": 200,
            "response": {
                "exists": exists, 
                "module": sanitize_module
            }
        }

    return {
        "version": API_VERSION,
        "status": 200,
        "response": {
            "module_info": module_info.__dict__(), 
            "module": sanitize_module
        }
    }

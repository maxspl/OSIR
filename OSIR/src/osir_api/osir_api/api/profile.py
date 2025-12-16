from fastapi import APIRouter
from osir_api.api.version import API_VERSION
from osir_lib.core.model.OsirProfileModel import OsirProfileModel
from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirConstants import OSIR_PATHS

from osir_api.api.exceptions import (
    ModuleNotFoundException,
    ModuleValidationException,
    ModuleLoadException,
    UnexpectedException
)

router = APIRouter()

@router.get("/profile")
def get_profiles():
    """Liste les profils OSIR disponibles"""
    try:
        profiles_dir = OSIR_PATHS.PROFILES_DIR
        if not profiles_dir.exists():
            raise Exception(f"Profiles directory not found: {profiles_dir}")
        
        profiles = []
        for profile_file in profiles_dir.glob("*.yml"):
            profiles.append(profile_file.name)
        
        response = {
            "version": API_VERSION,
            "status": 200,
            "response": {
                "profiles": profiles
            }
        }
        
        return response
    except Exception as e:
        raise UnexpectedException(str(e))

@router.get("/profile/exists/{profile_name}")
def profile_exists(profile_name: str):
    """Vérifie si un profil existe et retourne ses détails"""
    try:
        profile_path = FileManager.get_profile_path(profile_name)
        if not profile_path.exists():
            raise ModuleNotFoundException(profile_name)
        
        profile = OsirProfileModel.from_yaml(str(profile_path))
        
        response = {
            "version": API_VERSION,
            "status": 200,
            "response": profile.model_dump()
        }
        
        return response
    except FileNotFoundError:
        raise ModuleNotFoundException(profile_name)
    except Exception as e:
        raise UnexpectedException(str(e))

@router.get("/profile/run/{profile_name}")
def run_profile(profile_name: str):
    """Exécute un profil OSIR"""
    try:
        from osir_service.ipc.OsirIpcModel import OsirIpcModel
        from osir_service.ipc.OsirIpcClient import OsirIpcClient
        
        profile_path = FileManager.get_profile_path(profile_name)
        if not profile_path.exists():
            raise ModuleNotFoundException(profile_name)
        
        profile = OsirProfileModel.from_yaml(str(profile_path))
        
        client = OsirIpcClient()
        action = OsirIpcModel(action="exec_profile", profile=profile_name, case_path="/OSIR/share/cases/test_1")
        
        response = {
            "version": API_VERSION,
            "status": 200,
            "response": client.send(action)
        }
        
        return response
    except FileNotFoundError:
        raise ModuleNotFoundException(profile_name)
    except Exception as e:
        raise UnexpectedException(str(e))
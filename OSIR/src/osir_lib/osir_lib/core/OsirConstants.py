# PROFILES_DIR = "/OSIR/OSIR/configs/profiles/"
# MODULES_DIR = "/OSIR/OSIR/configs/modules/"
# CASES_DIR = "/OSIR/share/cases/"
# TOOL_DIR = "/OSIR/OSIR/bin/"
# PY_MODULES_DIR = "/OSIR/OSIR/src/osir_lib/osir_lib/modules"
# SETUP_DIR = "/OSIR/OSIR/setup/conf"


import os
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, computed_field

from osir_lib.core.OsirSingleton import singleton

@singleton
class Osir(BaseModel):
    @property
    def VERSION(self):
        return 1.0


@singleton
class OsirPaths(BaseModel):
    """
    Modèle Pydantic pour définir et résoudre les chemins basés sur OSIR_HOME.
    """
    
    # 1. Récupération de la variable d'environnement (optionnelle)
    # L'utilisation de Field(default_factory=...) permet de définir la valeur par défaut 
    # de manière dynamique (au moment de l'instanciation)
    osir_home_env: Optional[str] = Field(
        default_factory=lambda: os.getenv("OSIR_HOME")
    )

    # 2. Définition du chemin de base pour la construction des chemins absolus
    @computed_field
    @property
    def base_dir(self) -> Path:
        if self.osir_home_env:
            return Path(self.osir_home_env)
        else:
            # Si OSIR_HOME est vide, on utilise la racine '/' pour rester cohérent avec les chemins absolus codés en dur
            return Path("/") 

    # 3. Définition des chemins absolus en utilisant le chemin de base
    
    @computed_field
    @property
    def PROFILES_DIR(self) -> Path:
        if self.osir_home_env:
            return self.base_dir.joinpath("OSIR/configs/profiles/")
        return Path("/OSIR/OSIR/configs/profiles/")

    @computed_field
    @property
    def MODULES_DIR(self) -> Path:
        if self.osir_home_env:
            return self.base_dir.joinpath("OSIR/configs/modules/")
        return Path("/OSIR/OSIR/configs/modules/")

    # Répétez ce modèle pour tous les autres chemins...

    @computed_field
    @property
    def CASES_DIR(self) -> Path:
        if self.osir_home_env:
            return self.base_dir.joinpath("OSIR/share/cases/")
        return Path("/OSIR/share/cases/")

    @computed_field
    @property
    def TOOL_DIR(self) -> Path:
        if self.osir_home_env:
            return self.base_dir.joinpath("OSIR/bin/")
        return Path("/OSIR/OSIR/bin/")

    @computed_field
    @property
    def PY_MODULES_DIR(self) -> Path:
        if self.osir_home_env:
            return self.base_dir.joinpath("OSIR/src/osir_lib/osir_lib/modules")
        return Path("/OSIR/OSIR/src/osir_lib/osir_lib/modules")

    @computed_field
    @property
    def SETUP_DIR(self) -> Path:
        if self.osir_home_env:
            return self.base_dir.joinpath("OSIR/setup/conf")
        return Path("/OSIR/setup/conf")

    @computed_field
    @property
    def LOG_DIR(self) -> Path:
        if self.osir_home_env:
            return self.base_dir.joinpath("OSIR/share/log")
        return Path("/OSIR/share/log")
    
OSIR_PATHS = OsirPaths() 
OSIR = Osir()
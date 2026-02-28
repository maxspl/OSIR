import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, computed_field

from osir_lib.core.OsirSingleton import singleton


@singleton
class Osir(BaseModel):
    """
        Core metadata class for the OSIR framework.
    """
    @property
    def VERSION(self):
        """
            Returns the current version of the OSIR framework.
        """
        return 1.0


@singleton
class OsirPaths(BaseModel):
    """
        Pydantic-based path manager for resolving OSIR system directories.
    """

    osir_home_env: Optional[str] = Field(
        default_factory=lambda: os.getenv("OSIR_HOME")
    )

    @computed_field
    @property
    def base_dir(self) -> Path:
        """
            Calculates the root directory used as a prefix for all relative paths.

            If the 'OSIR_HOME' environment variable is set, it serves as the root. 

            Returns:
                Path: The resolved base directory.
        """
        if self.osir_home_env:
            return Path(self.osir_home_env)
        else:
            return Path("/")

    @computed_field
    @property
    def PROFILES_DIR(self) -> Path:
        """
            Resolves the directory containing ingestion and processing profiles.
        """
        if self.osir_home_env:
            return self.base_dir.joinpath("OSIR/configs/profiles/")
        return Path("/OSIR/OSIR/configs/profiles/")

    @computed_field
    @property
    def MODULES_DIR(self) -> Path:
        """
            Resolves the directory where individual tool module configurations reside.
        """
        if self.osir_home_env:
            return self.base_dir.joinpath("OSIR/configs/modules/")
        return Path("/OSIR/OSIR/configs/modules/")

    @computed_field
    @property
    def CASES_DIR(self) -> Path:
        """
            Resolves the shared storage location for case data and forensic outputs.
        """
        if self.osir_home_env:
            return self.base_dir.joinpath("share/cases/")
        return Path("/OSIR/share/cases/")

    @computed_field
    @property
    def TOOL_DIR(self) -> Path:
        """
            Resolves the binary directory where external forensic tools are stored.
        """
        if self.osir_home_env:
            return self.base_dir.joinpath("OSIR/bin/")
        return Path("/OSIR/OSIR/bin/")

    @computed_field
    @property
    def PY_MODULES_DIR(self) -> Path:
        """
            Resolves the location of internal Python library modules.
        """
        if self.osir_home_env:
            return self.base_dir.joinpath("OSIR/src/osir_lib/osir_lib/modules")
        return Path("/OSIR/OSIR/src/osir_lib/osir_lib/modules")

    @computed_field
    @property
    def SETUP_DIR(self) -> Path:
        """
            Resolves the directory containing system setup and initialization files.
        """
        if self.osir_home_env:
            return self.base_dir.joinpath("setup/conf")
        return Path("OSIR/setup/conf")

    @computed_field
    @property
    def LOG_DIR(self) -> Path:
        """
            Resolves the centralized directory for OSIR log files.
        """
        if self.osir_home_env:
            return self.base_dir.joinpath("share/log")
        return Path("/OSIR/share/log")


OSIR_PATHS = OsirPaths()
OSIR = Osir()

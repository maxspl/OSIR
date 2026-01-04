import os
from pathlib import Path
import yaml
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

class FileManager:

    @staticmethod
    def _get_file_path(name: str, base_dir: Path, raise_error: bool = True) -> Path:
        """
        Méthode privée générique pour la recherche de fichiers YAML.
        Utilise pathlib.rglob pour une recherche récursive efficace.
        
        Args:
            name (str): Le nom du fichier (avec ou sans .yml).
            base_dir (Path): Le répertoire de base où effectuer la recherche.

        Returns:
            Path: Le chemin absolu du fichier trouvé.
            
        Raises:
            FileNotFoundError: Si le fichier n'est pas trouvé.
        """
        base_path = base_dir 
        candidate = base_path / name
        if candidate.exists() and candidate.is_file():
            return candidate
        
        def case_insensitive_pattern(filename: str) -> str:
            return "".join(f"[{c.lower()}{c.upper()}]" if c.isalpha() else c for c in filename)

        pattern = case_insensitive_pattern(name)

        for path in base_dir.rglob(pattern):
            if path.is_file():
                return path
            
        logger.error(f"No {name} in directory {base_path}")
        if raise_error:
            raise FileNotFoundError(f"No {name} in directory {base_path}")
        
        return None
    
    @staticmethod
    def get_module_path(module: str) -> Path:
        module = module if module.endswith('.yml') else module + '.yml'
        return FileManager._get_file_path(module, OSIR_PATHS.MODULES_DIR)

    @staticmethod
    def get_profile_path(profile: str, raise_error: bool = True) -> Path:
        profile = profile if profile.endswith('.yml') else profile + '.yml'
        return FileManager._get_file_path(profile, OSIR_PATHS.PROFILES_DIR, raise_error)
    
    @staticmethod
    def get_config_path(config: str) -> Path:
        config = config if config.endswith('.yml') else config + '.yml'
        return FileManager._get_file_path(config, OSIR_PATHS.SETUP_DIR)
    
    @staticmethod
    def resolve_modules_parent_dir(modules):
        """
        Convert a list of module filenames to their relative paths from the base modules directory.

        Args:
            modules (list[str]): A list of module file names (e.g., "foo.yml").

        Returns:
            list[str]: Relative paths under the modules directory (e.g., "windows/foo.yml").
        """

        paths = []
        for root, _, files in os.walk(OSIR_PATHS.MODULES_DIR):
            for file in files:
                for module in modules:
                    if file == module:
                        # Get the relative path by removing the MODULES_DIR part from the full path
                        relative_path = os.path.relpath(os.path.join(root, file), OSIR_PATHS.MODULES_DIR)
                        paths.append(relative_path)
        return paths
    
    @staticmethod
    def get_files_in_cases(directory):
        """
        Get a list of files in a given directory (recursive).

        Args:
            directory (str): The directory to search for files.

        Returns:
            list[str]: A list of relative file paths found in the directory.
        """
        return [
            os.path.relpath(os.path.join(root, file), directory)
            for root, _, files in os.walk(directory)
            for file in files
        ]

    @staticmethod
    def get_yaml_files(directory, relative=False):
        """
        Get a list of .yml files in a given directory recursively.

        Args:
            directory (str): The directory to search for .yml files.
            relative (bool): If True, return paths relative to `directory`. If False, return basenames.

        Returns:
            list[str]: A list of YAML file paths or basenames.
        """
        yaml_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.yml'):
                    path = os.path.join(root, file)
                    yaml_files.append(os.path.relpath(path, directory) if relative else file)
        return yaml_files

    @staticmethod
    def get_cases(directory):
        """
        Get a list of subdirectories in a given directory.

        Args:
            directory (str): The directory to search.

        Returns:
            list[str]: A list of subdirectory names.
        """
        return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

    @staticmethod
    def get_cases_path(case_name: str) -> Path | None:
        case_path = OSIR_PATHS.CASES_DIR / case_name
        return case_path if case_path.exists() else None

    @staticmethod
    def load_yaml_file(filepath):
        """
        Load and parse content from a YAML file.

        Args:
            filepath (str): The path to the YAML file.

        Returns:
            dict: The parsed YAML content.
        """
        with open(filepath, 'r') as file:
            return yaml.safe_load(file)
    
    @staticmethod
    def create_case(directory: str, case_name: str):
        """
        Create a new case directory and.
        Args:
            directory (str): The directory where the case will be created.
            case_name (str): The name of the case (will be the directory name).
        Returns:
            str: The path to the created case directory.
        Raises:
            FileExistsError: If the case directory already exists.
        """
        case_path = os.path.join(directory, case_name)

        if os.path.exists(case_path):
            return ('exists', case_path)

        os.makedirs(case_path)

        return ('created', case_path)


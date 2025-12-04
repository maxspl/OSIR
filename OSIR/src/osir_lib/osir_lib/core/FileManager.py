import os
import yaml
from osir_lib.core import StaticVars
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

class FileManager:
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
        for root, _, files in os.walk(StaticVars.MODULES_DIR):
            for file in files:
                for module in modules:
                    if file == module:
                        # Get the relative path by removing the MODULES_DIR part from the full path
                        relative_path = os.path.relpath(os.path.join(root, file), StaticVars.MODULES_DIR)
                        paths.append(relative_path)
        return paths
    
    @staticmethod
    def get_module_path(module: str):
        module = module if module.endswith('.yml') else module + '.yml'

        candidate = os.path.join(StaticVars.MODULES_DIR, module)
        if os.path.exists(candidate):
            return candidate

        for root, dirs, files in os.walk(StaticVars.MODULES_DIR):
            for file in files:
                if file == module:
                    return os.path.join(root, file)
                
        logger.error(f"No module found with name {module} in directory {StaticVars.MODULES_DIR}")
        
        raise FileNotFoundError(f"No module found with name {module} in directory {StaticVars.MODULES_DIR}")

    @staticmethod
    def get_profile_path(profile: str):
        profile = profile if profile.endswith('.yml') else profile + '.yml'

        candidate = os.path.join(StaticVars.PROFILES_DIR, profile)
        if os.path.exists(candidate):
            return candidate

        for root, dirs, files in os.walk(StaticVars.PROFILES_DIR):
            for file in files:
                if file == profile:
                    return os.path.join(root, file)
                
        logger.error(f"No profile found with name {profile} in directory {StaticVars.PROFILES_DIR}")
        
        raise FileNotFoundError(f"No profile found with name {profile} in directory {StaticVars.PROFILES_DIR}")


    @staticmethod
    def full_path_module(module_relative_path: str):
        return os.path.join(StaticVars.MODULES_DIR, module_relative_path)

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
            return ('Exists', case_path)

        os.makedirs(case_path)

        return ('Created', case_path)


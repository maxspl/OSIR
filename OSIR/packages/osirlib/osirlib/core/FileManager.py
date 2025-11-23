import os
import yaml


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
        MODULES_DIR = "/OSIR/OSIR/configs/modules/"
        paths = []
        for root, _, files in os.walk(MODULES_DIR):
            for file in files:
                for module in modules:
                    if file == module:
                        # Get the relative path by removing the MODULES_DIR part from the full path
                        relative_path = os.path.relpath(os.path.join(root, file), MODULES_DIR)
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
            raise FileExistsError(f"Case '{case_name}' already exists in '{directory}'.")

        os.makedirs(case_path)

        return case_path


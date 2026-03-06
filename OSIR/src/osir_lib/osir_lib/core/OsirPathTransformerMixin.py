import hashlib
from pathlib import Path, PureWindowsPath
from typing import Optional, Callable

from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()


class OsirPathTransformerMixin:
    """
        Mixin centralizing the path transformation logic for the OSIR framework.
    """

    def update(self):
        """
            Abstract method intended to be implemented by child models.
        """
        raise NotImplementedError("Each model must implement its own finalization logic.")

    def _wsl_suffix(self, in_path: str) -> Optional[str]:
        """
            Transforms a standard OSIR path into a format suitable for WSL.

            Args:
                in_path (str): The original Linux-style path.

            Returns:
                Optional[str]: The translated Windows path for WSL, or 'Error' if '/share' is missing.
        """
        if not in_path:
            return None
        search_keyword = '/share'
        position = in_path.find(search_keyword)
        if position != -1:
            path_to_replace = in_path[:position]
            UNC_input_path = in_path.replace(path_to_replace, "{master_host}")
            return str(PureWindowsPath(Path(UNC_input_path)))
        logger.error("Error: '/share' not found in the path")
        return "Error"

    def _windows_suffix(self, in_path: str) -> Optional[str]:
        """
            Converts a Linux mount path into a Windows UNC (Universal Naming Convention) path.

            Args:
                in_path (str): The original Linux-style path.

            Returns:
                Optional[str]: The converted UNC path, or 'Error' if incompatible.
        """
        if "{master_host}" in in_path:
            return in_path
        if in_path:
            search_keyword = '/share'
            position = in_path.find(search_keyword)
            if position != -1:
                path_to_replace = in_path[:position + 1]
                UNC_input_path = in_path.replace(path_to_replace, "\\\\{master_host}\\")
                # Convert path to Windows backslash format
                converted_UNC_input_path = str(PureWindowsPath(Path(UNC_input_path)))
                return converted_UNC_input_path
            else:
                return "Error"
        else:
            return None

    def _windows_suffix_docker(self, in_path: str) -> Optional[str]:
        """
            Adjusts paths for forensic tools running inside Windows-based Docker containers.

            Args:
                in_path (str): The source path.

            Returns:
                Optional[str]: The path prefixed with the Windows C: drive.
        """
        if not in_path:
            return None
        return f"C:{PureWindowsPath(Path(in_path))}"

    def _get_suffix_fn(self) -> Optional[Callable[[str], Optional[str]]]:
        """
            Determines the appropriate transformation function based on the OS context.

            Returns:
                Optional[Callable]: The selected transformation function.
        """
        if not hasattr(self, "_context") or self._context is None:
            return None

        os_type = self._context.configuration.processor_os
        if os_type == 'unix':
            return None
        elif os_type == 'windows':
            return self._wsl_suffix if self._context.is_wsl else self._windows_suffix
        return None

    def apply_suffix(self, field_name: str, return_value: bool = False):
        """
            Retrieves a specific field's value, transforms it, and reassigns it.

            Args:
                field_name (str): The name of the attribute to transform (e.g., 'match', 'output_dir').
                return_value (bool): If True, returns the path instead of setting the attribute.
        """
        suffix_fn = self._get_suffix_fn()
        value = getattr(self, field_name, None)

        if suffix_fn and value:
            new_path = suffix_fn(str(value))
            if new_path and new_path != "Error":
                if return_value:
                    return Path(new_path)
                setattr(self, field_name, Path(new_path))

    def _hash_path(self, path: str) -> str:
        """
            Generates a unique MD5 hash for a file path.
        """
        return hashlib.md5(path.encode()).hexdigest()

    @staticmethod
    def safe_format(text: str, **kwargs) -> str:
        """
            Performs placeholder substitution in strings using direct replacement.

            Args:
                text (str): The template string (e.g., "results_{endpoint_name}.csv").
                **kwargs: Key-value pairs for substitution.

            Returns:
                str: The formatted string with placeholders replaced.
        """
        if not text:
            return text

        result = text
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        return result

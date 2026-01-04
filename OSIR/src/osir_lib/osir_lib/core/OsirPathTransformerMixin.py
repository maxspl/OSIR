import hashlib
import logging
from pathlib import Path, PureWindowsPath
from typing import Optional, Any, Callable

from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()

class OsirPathTransformerMixin:
    """Mixin centralisant la logique de transformation des chemins pour Osir."""

    def update(self):
        raise NotImplementedError("Chaque modèle doit implémenter sa propre logique de finalisation.")
    
    def _wsl_suffix(self, in_path: str) -> Optional[str]:
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
        if in_path:  # None in some cases (output file for example)
            # The keyword to search for in the path
            search_keyword = '/share'
            # Find the position of '/share' in the string
            position = in_path.find(search_keyword)
            # Check if '/share' is found
            if position != -1:
                # Add the length of '/share' to include it in the result
                path_to_replace = in_path[:position + 1]
                UNC_input_path = in_path.replace(path_to_replace, "\\\\{master_host}\\")
                converted_UNC_input_path = str(PureWindowsPath(Path(UNC_input_path)))  # Convert path to window
                return converted_UNC_input_path
            else:
                # logger.error("Error: '/share' not found in the path")
                return "Error"
        else:
            return None

    def _windows_suffix_docker(self, in_path: str) -> Optional[str]:
        if not in_path:
            return None
        return f"C:{PureWindowsPath(Path(in_path))}"

    def _get_suffix_fn(self) -> Optional[Callable[[str], Optional[str]]]:
        """Détermine la fonction à utiliser selon le contexte de l'OS."""
        if not hasattr(self, "_context") or self._context is None:
            return None
            
        os_type = self._context.processor_os
        if os_type == 'unix':
            return None
        elif os_type == 'windows':
            return self._wsl_suffix if self._context.is_wsl else self._windows_suffix
        return None

    def apply_suffix(self, field_name: str):
        """Récupère la valeur du champ, la transforme et la réassigne."""
        suffix_fn = self._get_suffix_fn()
        value = getattr(self, field_name, None)
        
        if suffix_fn and value:
            new_path = suffix_fn(str(value))
            if new_path and new_path != "Error":
                setattr(self, field_name, Path(new_path))
    
    def _hash_path(self, path: str) -> str:
        return hashlib.md5(path.encode()).hexdigest()
    
    @staticmethod
    def safe_format(text: str, **kwargs) -> str:
        """Remplace les placeholders par injection directe sans passer par .format()"""
        if not text:
            return text
        
        result = text
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        return result
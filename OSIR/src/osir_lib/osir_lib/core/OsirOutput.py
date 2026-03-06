import hashlib
import os
from pathlib import Path
import re
import shutil
from typing import TYPE_CHECKING, Optional

from pydantic import PrivateAttr
from osir_lib.core.OsirPathTransformerMixin import OsirPathTransformerMixin
from osir_lib.core.model.OsirOutputModel import OsirOutputModel

if TYPE_CHECKING:
    from osir_lib.core.OsirModule import OsirModule

from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()


class OsirOutput(OsirOutputModel, OsirPathTransformerMixin):
    """
        Manages the generation, naming, and structural organization of forensic tool outputs.


        Attributes:
            _context (OsirModule): Private reference to the parent module for accessing 
                shared case metadata.
            output_prefix_no_endpoint (str): Internal storage for the naming prefix 
                excluding the endpoint name, used for regex matching during renames.
            updated (bool): Flag to ensure path transformations are only performed once.
    """
    _context: "OsirModule" = PrivateAttr()

    # TODO: Remove this and refactor _rename_items_recursively
    output_prefix_no_endpoint: Optional[str] = None
    updated: Optional[bool] = False

    # TODO: Not the best implemantation i think 
    output_file_without_suffix: Optional[str] = None
    output_dir_without_suffix: Optional[str] = None

    def _hash_path(self, path: str) -> str:
        """
            Generates an MD5 hash of a given path string.

            Args:
                path (str): The file path to hash.

            Returns:
                str: The hex digest of the path.
        """
        if not path:
            return ""
        return hashlib.md5(str(path).encode()).hexdigest()

    def update(self) -> "OsirOutput":
        """
            Resolves output templates and prepares the filesystem for result storage.

            Returns:
                OsirOutput: The instance with fully resolved and absolute paths.
        """
        if not self.updated:
            ctx = self._context

            replacements = {
                "endpoint_name": ctx.endpoint_name,
                "module": ctx.module,
                "input_file": ctx.input.get_input_name_safe(),
                "input_path_hash": self._hash_path(str(ctx.input.match)),
                "case_path": ctx.case_path
            }
            
            base_output_path = Path(ctx.case_path) / ctx.module

            if self.output_dir and "{case_path}" in self.output_dir:
                self.output_dir = self.safe_format(self.output_dir, **replacements)
            # Resolve Directory Template
            elif self.output_dir:
                full_template = str(base_output_path / self.output_dir)
                self.output_dir = self.safe_format(full_template, **replacements)
            else:
                self.output_dir = base_output_path

            # Resolve Filename Template
            if self.output_file:
                formatted_filename = self.safe_format(self.output_file, **replacements)
                self.output_file = str(Path(self.output_dir) / formatted_filename)
            
            self.output_dir_without_suffix = self.output_dir
            self.output_file_without_suffix = self.output_file
            self.apply_suffix("output_dir")
            self._ensure_output_dir_exists()
            self.apply_suffix("output_file")

            # Handle Naming Prefixes for recursive organization
            if self.output_prefix:
                self.output_prefix_no_endpoint = self.safe_format(self.output_prefix,
                                                                  **{k: v for k, v in replacements.items() if k != 'endpoint_name'})
                self.output_prefix = self.safe_format(self.output_prefix, **replacements)

            self.updated = True

            return self
        return self

    def _ensure_output_dir_exists(self):
        """
            Creates if the output directory exists on the master filesystem.
        """
        if self._context.configuration.processor_os == 'unix' and self._context.configuration.type != 'post_parsing':
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def _rename_items_recursively(self):
        """
            Recursively applies the OSIR naming prefix to all files and folders in the output.
        """
        prefix = os.path.basename(self._context.output.output_prefix)

        # Build regex to avoid double-renaming items that already have a valid prefix
        prefix_extented = re.compile("^" + self._context.output.output_prefix_no_endpoint.replace("{endpoint_name}", ".*"))

        for root, dirs, files in os.walk(self._context.output.output_dir, topdown=True):
            # Process files within the current directory
            for file in files:
                if not prefix_extented.match(file):
                    original_file_path = os.path.join(root, file)
                    new_file_name = prefix + file
                    new_file_path = os.path.join(root, new_file_name)
                    os.rename(original_file_path, new_file_path)

            # Process sub-directories
            for i, dir in enumerate(dirs):
                if not prefix_extented.match(dir):
                    original_dir_path = os.path.join(root, dir)
                    new_dir_name = prefix + dir
                    new_dir_path = os.path.join(root, new_dir_name)
                    shutil.move(original_dir_path, new_dir_path)
                    # Update directory list to ensure walking continues with the new path
                    dirs[i] = new_dir_name

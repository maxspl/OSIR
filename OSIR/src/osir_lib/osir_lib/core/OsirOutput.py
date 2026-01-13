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
    _context: "OsirModule" = PrivateAttr() 

    # TODO: Remove this and refactor _rename_items_recursively
    output_prefix_no_endpoint: Optional[str] = None
    updated: Optional[bool] = False

    def _hash_path(self, path: str) -> str:
        if not path: return ""
        return hashlib.md5(str(path).encode()).hexdigest()

    def update(self) -> "OsirOutput":
        if not self.updated:
            ctx = self._context
        
            replacements = {
                "endpoint_name": ctx.endpoint_name,
                "module": ctx.module,
                "input_file": ctx.input.get_input_name_safe(),
                "input_path_hash": self._hash_path(str(ctx.input.match)),
            }
            # logger.debug(ctx.model_dump_json(indent=4))
            base_output_path = Path(ctx.case_path) / ctx.module
            
            if self.output_dir:
                full_template = str(base_output_path / self.output_dir)
                self.output_dir  = self.safe_format(full_template, **replacements)
            else:
                self.output_dir = base_output_path

            if self.output_file:
                formatted_filename = self.safe_format(self.output_file, **replacements)
                self.output_file = str(Path(self.output_dir) / formatted_filename)

            self.apply_suffix("output_dir")
            self._ensure_output_dir_exists()
            self.apply_suffix("output_file")

            if self.output_prefix:
                self.output_prefix_no_endpoint = self.safe_format(self.output_prefix,
                    **{k: v for k, v in replacements.items() if k != 'endpoint_name'})
                self.output_prefix = self.safe_format(self.output_prefix, **replacements)

            self.updated = True

            return self
        return self
    def _ensure_output_dir_exists(self):
        if self._context.processor_os == 'unix':
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def _rename_items_recursively(self):
        """
        Recursively renames files and directories in the output directory with a specified prefix to organize output data.
        """
        prefix = os.path.basename(self._context.output.output_prefix)
        
        # First, we need to process all directories from the bottom of the directory tree
        prefix_extented = re.compile("^" + self._context.output.output_prefix_no_endpoint.replace("{endpoint_name}", ".*"))  # Replace the endpoint name in the prefix with regex to avoid renaming files of other endpoints
        for root, dirs, files in os.walk(self._context.output.output_dir, topdown=True):
            # Rename all files in the current directory
            for file in files:
                if not prefix_extented.match(file):  # Check if the file is not already renamed
                    original_file_path = os.path.join(root, file)
                    new_file_name = prefix + file
                    new_file_path = os.path.join(root, new_file_name)
                    os.rename(original_file_path, new_file_path)
            # Rename directories only if they are not already renamed
            # We check and rename directories after processing the files to avoid path errors
            for i, dir in enumerate(dirs):
                if not prefix_extented.match(dir):
                    original_dir_path = os.path.join(root, dir)
                    new_dir_name = prefix + dir
                    new_dir_path = os.path.join(root, new_dir_name)
                    shutil.move(original_dir_path, new_dir_path)
                    dirs[i] = new_dir_name  # Update the directory list with the new name to correctly handle nested directories
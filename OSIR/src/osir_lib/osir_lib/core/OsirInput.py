from pathlib import Path
from typing import TYPE_CHECKING, Optional

from pydantic import PrivateAttr
from osir_lib.core.OsirPathTransformerMixin import OsirPathTransformerMixin
from osir_lib.core.model.OsirInputModel import OsirInputModel

if TYPE_CHECKING:
    from osir_lib.core.OsirModule import OsirModule


class OsirInput(OsirInputModel, OsirPathTransformerMixin):
    """
        Manages the input data source for an OSIR module, handling path resolution and transformation.

        Attributes:
            _context (OsirModule): Private reference to the parent module context.
            match (Path): The original match file path.
            match_updated (Optional[Path]): The resolved path after transformations are applied.
    """
    _context: "OsirModule" = PrivateAttr()
    match: Path
    match_updated: Optional[Path] = None

    # TODO: Remove this
    updated: Optional[bool] = False

    def get_input_name_safe(self) -> str:
        """
            Returns a truncated and filesystem-safe version of the input filename.

            Returns:
                str: The sanitized filename string.
        """
        if self.match:
            name = Path(str(self.match)).name
            return name[:255]  # Linux filesystem limit
        return ''

    def update(self) -> "OsirInput":
        """
            Applies path transformation logic to the input match.

            Returns:
                OsirInput: The current instance with updated path information.
        """
        if not self.updated:
            updated_value = self.apply_suffix("match", return_value=True)
            self.match_updated = updated_value if updated_value else self.match
            self.updated = True
        return self

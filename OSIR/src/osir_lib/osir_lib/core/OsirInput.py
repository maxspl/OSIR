from pathlib import Path
from typing import TYPE_CHECKING, Optional

from pydantic import PrivateAttr
from osir_lib.core.OsirPathTransformerMixin import OsirPathTransformerMixin
from osir_lib.core.model.OsirInputModel import OsirInputModel

if TYPE_CHECKING:
    from osir_lib.core.OsirModule import OsirModule

class OsirInput(OsirInputModel, OsirPathTransformerMixin):
    _context: "OsirModule" = PrivateAttr() 
    match: Path
    match_updated: Optional[Path] = None

    # TODO: Remove this
    updated: Optional[bool] = False

    def get_input_name_safe(self) -> str:
        """Retourne un nom de fichier tronqué et sûr."""
        if self.match:
            name = Path(str(self.match)).name
            return name[:255] # Limite Linux
        return ''

    def update(self) -> "OsirInput":
        if not self.updated:
            updated_value = self.apply_suffix("match", return_value=True)
            self.match_updated = updated_value if updated_value else self.match
            self.updated = True
        return self
        
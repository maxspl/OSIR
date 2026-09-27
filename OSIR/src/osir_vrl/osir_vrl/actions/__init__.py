from typing import Union
from .OsirVrlSet       import OsirVrlSet
from .OsirVrlTranslate import OsirVrlTranslate
from .OsirVrlDelete    import OsirVrlDelete
from .OsirVrlCustom    import OsirVrlCustom

Action = Union[OsirVrlSet, OsirVrlTranslate, OsirVrlDelete, OsirVrlCustom]

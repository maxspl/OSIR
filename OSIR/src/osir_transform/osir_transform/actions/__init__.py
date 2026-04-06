from typing import Union
from .SetAction       import SetAction
from .TranslateAction import TranslateAction
from .DeleteAction    import DeleteAction
from .CustomAction    import CustomAction

Action = Union[SetAction, TranslateAction, DeleteAction, CustomAction]

__all__ = ["SetAction", "TranslateAction", "DeleteAction", "CustomAction", "Action"]

OSIR_ACTIONS: dict[str, dict] = {}


def register_action(*action_names, required_fields: list[str] = None):
    """
    Decorator that registers a method as a handler for one or more IPC action names.

    Args:
        *action_names: One or more action name strings to bind to this handler.
        required_fields: List of OsirIpcRequest fields that must be present and non-empty.
    """
    def decorator(func):
        for name in action_names:
            OSIR_ACTIONS[name] = {
                "handler": func,
                "required_fields": required_fields or [],
            }
        return func
    return decorator
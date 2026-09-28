"""Contract tests for the osir_service IPC action registry.

The registry (OSIR_ACTIONS) is the backbone of the whole framework: the
FastAPI layer and the web UI both go through it. These tests lock down the
list of registered actions and their required fields so a rename or an
accidental removal is caught by CI.
"""
import pytest

# Importing OsirIpc executes every @register_action decorator.
from osir_service.ipc.model.OsirAction import OSIR_ACTIONS  # noqa: F401
import osir_service.ipc.OsirIpc  # noqa: F401  (populates the registry)

# action -> required fields (None means "no required field")
EXPECTED_ACTIONS = {
    "socket_on": [],
    "exec_module": ["modules", "case_path"],
    "exec_profile": ["profile"],
    "create_handler": ["case_name"],
    "create_advanced_handler": ["case_name"],
    "delete_handler": ["handler_uuid"],
    "stop_handler": ["handler_uuid"],
    "get_system_metrics": [],
    "restart_task": ["task_id"],
    "create_case": ["case_name"],
    "get_cases": [],
    "get_tasks": [],
    "get_task_stats": [],
    "get_task_log": ["task_id"],
    "get_handler_status": ["handler_id"],
    "get_case_handler": ["case_name"],
    "get_handler_task_info": [],
    "get_modules": [],
    "get_module_info": ["modules"],
    "files_list": [],
    "files_delete": ["body"],
    "files_rename": ["body"],
    "files_copy": ["body"],
    "files_move": ["body"],
    "files_archive": ["body"],
    "files_unarchive": ["body"],
    "files_create_folder": ["body"],
    "files_download": ["path"],
    "files_search": ["path"],
    "tus_upload_options": [],
    "tus_upload_post": [],
    "tus_upload_patch": [],
    "tus_upload_head": ["uuid"],
}


def test_registry_contains_every_expected_action():
    missing = set(EXPECTED_ACTIONS) - set(OSIR_ACTIONS)
    assert not missing, f"actions no longer registered: {sorted(missing)}"


def test_registry_has_no_unexpected_action():
    extra = set(OSIR_ACTIONS) - set(EXPECTED_ACTIONS)
    assert not extra, (
        f"new actions registered: {sorted(extra)} — update EXPECTED_ACTIONS "
        "in tests/osir_service/test_ipc_registry.py"
    )


@pytest.mark.parametrize("action", sorted(EXPECTED_ACTIONS))
def test_action_required_fields(action):
    assert OSIR_ACTIONS[action]["required_fields"] == EXPECTED_ACTIONS[action], (
        f"required_fields changed for '{action}'"
    )


@pytest.mark.parametrize("action", sorted(EXPECTED_ACTIONS))
def test_action_handler_is_bound(action):
    assert callable(OSIR_ACTIONS[action]["handler"]), f"no handler bound for '{action}'"

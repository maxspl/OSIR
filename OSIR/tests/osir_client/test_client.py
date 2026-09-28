"""Coverage of every public method of the osir_client library.

The `bridge` fixture (tests/conftest.py) intercepts the client's `requests`
calls and forwards them to the real FastAPI app (TestClient, stubbed IPC).
So these tests validate the client against the actual routes: if a route
moves or a payload changes, the client test fails — which is exactly what
we want to catch.
"""
import pytest

from osir_client.client.OsirClient import OsirClient
from osir_client.client.OsirCliCase import OsirCliCase
from osir_client.client.OsirCliHandler import OsirCliHandler
from osir_client.client.OsirCliStats import OsirCliStats

API_URL = "http://testserver"
CASE_NAME = "client_case"
PROFILE = "demo_profile.yml"


@pytest.fixture
def client(bridge) -> OsirClient:
    return OsirClient(api_url=API_URL)


@pytest.fixture
def case(client) -> OsirCliCase:
    """A case created through the client (its directory really exists)."""
    return client.cases.create(CASE_NAME)


# --- health / version --------------------------------------------------------

def test_is_active(client):
    assert client.is_active() is True


def test_check_version(client):
    # Must not raise, whatever the server version is.
    client._check_version()


# --- cases -------------------------------------------------------------------

def test_case_create(client, case):
    assert case.name == CASE_NAME
    assert case.case_uuid


def test_case_create_directory_on_disk(case):
    from osir_lib.core.OsirConstants import OSIR_PATHS
    assert (OSIR_PATHS.CASES_DIR / CASE_NAME).is_dir()


def test_case_get(client, case):
    # create() then get() must resolve the same case.
    found = client.cases.get(CASE_NAME)
    assert found.name == CASE_NAME
    assert found.case_uuid == case.case_uuid


def test_case_get_unknown(client):
    case = client.cases.get("nope_case")
    assert case.case_uuid is None  # not found: stays unconfigured, no crash


def test_case_list(client, case):
    assert client.cases.list() is None  # prints the table, returns nothing


# --- modules -------------------------------------------------------------------

def test_module_list(client, case):
    modules = case.modules.list(print=False)
    assert modules == ["bodyfile.yml"]


def test_module_exists(client, case):
    info = case.modules.exists("bodyfile.yml")
    assert isinstance(info, dict)
    assert info.get("module_name") == "bodyfile.yml"


def test_module_exists_missing(client, case):
    assert case.modules.exists("missing.yml") is None


def test_module_run_on_case(client, case):
    handler = case.modules.run("bodyfile.yml")
    assert isinstance(handler, OsirCliHandler)
    assert handler.handler_id


def test_module_run_on_file(client, case, tmp_path):
    from osir_lib.core.OsirConstants import OSIR_PATHS

    local = tmp_path / "evidence.evtx"
    local.write_bytes(b"\x02\x00\x00\x00fake-evtx")

    handler = case.modules.run("bodyfile.yml", input_path=str(local))
    assert isinstance(handler, OsirCliHandler)
    assert handler.handler_id
    # The file was chunk-uploaded into the case uploads directory.
    assert (OSIR_PATHS.CASES_DIR / CASE_NAME / "uploads" / local.name).read_bytes() == local.read_bytes()


def test_module_run_without_case(client):
    # A module manager with no case context logs an error and degrades.
    orphan = OsirCliCase()
    orphan._api = client
    assert orphan.modules.run("bodyfile.yml") is orphan.modules


def test_module_run_missing_input(client, case):
    handler = case.modules.run("bodyfile.yml", input_path="/does/not/exist.bin")
    assert not isinstance(handler, OsirCliHandler)  # degrades instead of raising


# --- profiles -------------------------------------------------------------------

def test_profile_list(client, case):
    profiles = case.profiles.list(print=False)
    assert profiles == [PROFILE]


def test_profile_exists(client, case):
    profile = case.profiles.exists(PROFILE)
    assert profile is not None
    assert PROFILE in (getattr(profile, "filename", None), )


def test_profile_exists_missing(client, case):
    assert case.profiles.exists("nope.yml") is None


def test_profile_run(client, case):
    handler = case.profiles.run(PROFILE)
    assert isinstance(handler, OsirCliHandler)
    assert handler.handler_id


# --- handlers -------------------------------------------------------------------

def test_handler_list(client, case):
    assert case.handlers.list() is not None  # prints, returns self


def test_handler_status(client, case):
    handler = case.modules.run("bodyfile.yml")
    result = handler.status()
    assert result is handler
    assert handler._status == "processing_done"


def test_handler_status_wait_end(client, case):
    handler = case.modules.run("bodyfile.yml")
    # The stub returns a finished handler, so wait_end returns immediately.
    result = handler.status(wait_end=True, timeout=5, interval=1)
    assert result._status in ("processing_done", "processing_failed")


# --- tasks -------------------------------------------------------------------

def test_task_list(client, case):
    assert case.tasks.list() is not None  # prints, returns self


def test_task_get_info(client, case):
    # Any task id works: the stub answers with a well-formed task record.
    task = case.tasks.get_task_info("00000000-0000-0000-0000-000000000001", print=False)
    assert task.task_id
    assert task.module == "bodyfile.yml"
    assert task.case_uuid


# --- stats -------------------------------------------------------------------

def test_stats_case(client, case):
    stats = OsirCliStats(client)._fetch_case_stats(CASE_NAME)
    assert stats["total"] == 1


def test_stats_handler(client, case):
    handler = case.modules.run("bodyfile.yml")
    stats = OsirCliStats(client)._fetch_handler_stats(handler.handler_id)
    assert stats["total"] == 1


def test_stats_show(client, case):
    # One-shot rendering must not raise nor loop.
    OsirCliStats(client).show(case_name=CASE_NAME)


# --- full workflow ------------------------------------------------------------

def test_end_to_end_workflow(client):
    """create case -> run module -> wait -> read tasks: the documented happy path."""
    case = client.cases.create("workflow_case")
    handler = case.modules.run("bodyfile.yml")
    handler.status(wait_end=True, timeout=5, interval=1)
    case.tasks.list()
    task = case.tasks.get_task_info("00000000-0000-0000-0000-000000000002", print=False)
    assert task is not None

"""
Root conftest for the OSIR test suite.

Responsibilities:
- Point every OSIR package at the repository sources (site-packages may hold
  stale copies) by putting each `src/<pkg>` dir at the front of sys.path.
- Isolate the filesystem: OSIR_HOME is redirected to a temp directory, so
  CASES_DIR / PROFILES_DIR / MODULES_DIR never touch a real share.
- Provide a fake IPC backend (a stand-in for the osir_service TCP socket) so
  the FastAPI routes can be exercised end-to-end over HTTP without Celery,
  PostgreSQL or RabbitMQ.
- Provide a `bridge` fixture that routes the Python client's `requests` calls
  into the FastAPI TestClient, so the client is tested against the real API.

NOTE: this module is imported by pytest before any test module, so the
environment and sys.path setup below runs before the first OSIR import.
"""
import base64
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

import pytest

TESTS_ROOT = os.path.dirname(os.path.abspath(__file__))
OSIR_ROOT = os.path.dirname(TESTS_ROOT)
SRC = os.path.join(OSIR_ROOT, "src")

# --- 1. Filesystem isolation (must happen before any osir import) ---------
OSIR_HOME = Path(tempfile.mkdtemp(prefix="osir-tests-"))
os.environ["OSIR_HOME"] = str(OSIR_HOME)
(OSIR_HOME / "share" / "cases").mkdir(parents=True)
_PROFILES = OSIR_HOME / "OSIR" / "configs" / "profiles"
_PROFILES.mkdir(parents=True)
(_PROFILES / "demo_profile.yml").write_text("modules: [bodyfile.yml]\n")
(OSIR_HOME / "OSIR" / "configs" / "modules").mkdir(parents=True)

# --- 2. Resolve packages on the repository sources ------------------------
for _pkg in ("osir_lib", "osir_service", "osir_api", "osir_client", "osir_vrl"):
    _path = os.path.join(SRC, _pkg)
    if os.path.isdir(_path) and _path not in sys.path:
        sys.path.insert(0, _path)

from fastapi.testclient import TestClient  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402

# Import every OSIR package NOW, against the repository sources. When pytest
# later inserts the tests/osir_* folders into sys.path (rootdir collection),
# an empty tests/osir_client/ would otherwise shadow the real package as a
# namespace package. Importing here pins the right modules in sys.modules.
import osir_client  # noqa: F401,E402
import osir_vrl  # noqa: F401,E402
import osir_api  # noqa: F401,E402
import osir_lib  # noqa: F401,E402
import osir_service  # noqa: F401,E402

from osir_api.OsirApi import app  # noqa: E402  (also imports all route modules)
from osir_api.api.OsirApiMetadata import API_VERSION  # noqa: E402
from osir_lib.core.FileManager import FileManager  # noqa: E402
from osir_lib.core.OsirConstants import OSIR_PATHS  # noqa: E402
from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse  # noqa: E402

# ---------------------------------------------------------------------------
# Fake data factories
# ---------------------------------------------------------------------------

CASE_NAME = "demo_case"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_case(name: str = CASE_NAME) -> dict:
    return {"case_uuid": str(uuid4()), "name": name, "exists_on_disk": True}


def make_handler(case_uuid: str, status: str = "processing_done") -> dict:
    return {
        "handler_id": str(uuid4()),
        "case_uuid": case_uuid,
        "modules": ["bodyfile.yml"],
        "task_id": [],
        "task_count": 0,
        "processing_status": status,
        "created_at": _now(),
    }


def make_task(case_uuid: str, handler_id: str) -> dict:
    return {
        "task_id": str(uuid4()),
        "case_uuid": case_uuid,
        "handler_id": handler_id,
        "agent": "test-agent",
        "module": "bodyfile.yml",
        "input": "/tmp/input.evtx",
        "output": None,
        "processing_status": "task_created",
        "timestamp": _now(),
        "trace": {"logs": []},
    }


def make_metrics() -> dict:
    return {"agent": "test-agent", "ts": _now(), "cpu_pct": 12.5, "mem_pct": 40.0}


def make_direntry(name: str = "hello.txt", type_: str = "file") -> dict:
    return {
        "dir": "demo_case://uploads",
        "basename": name,
        "extension": name.rsplit(".", 1)[-1] if "." in name else "",
        "path": f"demo_case://uploads/{name}",
        "storage": "demo_case",
        "type": type_,
        "visibility": "visible",
    }


# ---------------------------------------------------------------------------
# Fake IPC backend
# ---------------------------------------------------------------------------

def _envelope(payload, message: str = "Everything is working as it should!") -> dict:
    return {"version": API_VERSION, "status": 200, "message": message, "response": payload}


def make_fake_ipc():
    """Build a callable with the OsirIpcCall(action, params, response_only) signature.

    Dispatches every action used by the API routes and returns payloads that
    satisfy the route response_models. State (cases created on disk) mimics
    the real service where the API layer depends on it.
    """
    case = make_case()
    cases = [make_case(name=CASE_NAME)]  # cases known to the fake backend
    handler = make_handler(case["case_uuid"])
    task = make_task(case["case_uuid"], handler["handler_id"])
    known_modules = {"bodyfile.yml"}

    def ipc_call(action, params=None, response_only=False):
        params = params or {}
        body = params.get("body", {})

        if action == "socket_on":
            payload = {}
        elif action == "get_cases":
            payload = cases
        elif action == "create_case":
            # The real IPC handler also creates the case directory.
            FileManager.create_case(str(OSIR_PATHS.CASES_DIR), params["case_name"])
            new_case = {"case_uuid": str(uuid4()), "name": params["case_name"], "exists_on_disk": True}
            cases.append(new_case)
            payload = new_case
        elif action == "get_case_handler":
            payload = [make_handler(case["case_uuid"])]
        elif action == "get_tasks":
            payload = {
                "tasks": [task],
                "total": 1,
                "page": params.get("page", 1),
                "page_size": params.get("page_size", 20),
                "total_pages": 1,
            }
        elif action == "get_task_stats":
            payload = {"total": 1, "per_status": {"task_created": 1}, "per_module": {"bodyfile.yml": 1}}
        elif action == "get_modules":
            payload = ["bodyfile.yml"]
        elif action == "get_module_info":
            # The real handler answers {} for unknown modules (logged as an error).
            payload = {m: ({"module_name": m} if m in known_modules else {}) for m in params.get("modules", [])}
        elif action == "get_handler_status":
            payload = handler
        elif action == "get_handler_task_info":
            payload = [task]
        elif action == "get_task_log":
            payload = task
        elif action == "restart_task":
            payload = {"task_id": params["task_id"]}
        elif action in ("exec_profile", "create_handler", "create_advanced_handler", "delete_handler"):
            payload = make_handler(case["case_uuid"], status="processing_started")
        elif action == "stop_handler":
            payload = {"handler_id": params.get("handler_uuid"), "stopped": True}
        elif action == "get_system_metrics":
            payload = [make_metrics()]
        elif action == "files_list":
            payload = {"storages": ["demo_case://"], "dirname": params.get("path", ""),
                       "files": [make_direntry()], "read_only": False}
        elif action == "files_delete":
            payload = {"files": [], "storages": ["demo_case://"], "read_only": False,
                       "dirname": body.get("path", ""), "deleted": [make_direntry()]}
        elif action in ("files_rename", "files_copy", "files_move", "files_archive",
                        "files_unarchive", "files_create_folder"):
            payload = {"files": [make_direntry()], "storages": ["demo_case://"],
                       "read_only": False, "dirname": body.get("path", "")}
        elif action == "files_download":
            payload = {"filename": "hello.txt",
                       "content": base64.b64encode(b"hello world").decode(),
                       "mimeType": "text/plain"}
        elif action == "files_search":
            payload = {"dirname": params.get("path", ""), "files": [make_direntry()],
                       "storages": ["demo_case://"]}
        elif action == "files_save":
            payload = {}
        elif action == "tus_upload_options":
            return JSONResponse(content=_envelope({}), headers={"Tus-Resumable": "1.0.0"})
        elif action == "tus_upload_post":
            return JSONResponse(
                content=_envelope({"uuid": str(uuid4())}),
                headers={"Tus-Resumable": "1.0.0", "Location": "/api/files/upload/1234"},
            )
        elif action == "tus_upload_head":
            return JSONResponse(
                content=_envelope({"upload_offset": 4}),
                headers={"Tus-Resumable": "1.0.0", "Upload-Offset": "4"},
            )
        else:
            raise AssertionError(f"fake IPC: unexpected action '{action}'")

        return payload if response_only else _envelope(payload)

    return ipc_call


class FakeOsirSocket:
    """Stand-in for OsirSocket in the tus PATCH route (used directly there)."""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def send(self, request):
        return OsirIpcResponse(
            status=200,
            message="chunk stored",
            response={"headers": {"Upload-Offset": "4"}},
        ).model_dump_json()


_IPC_MODULES = [
    "OsirApiCase", "OsirApiModule", "OsirApiProfile", "OsirApiHandler",
    "OsirApiTask", "OsirApiStatus", "OsirApiFiles", "OsirApiTus", "OsirApiMonitoring",
]


@pytest.fixture
def fake_ipc(monkeypatch):
    """Replace OsirIpcCall in every route module (and OsirSocket in the tus router).

    OsirApi.py loads the route modules with importlib under ad-hoc names, so
    they are not in sys.modules as "osir_api.api.<name>". The reliable way to
    reach their namespaces is the endpoint functions' __globals__.
    """
    ipc = make_fake_ipc()
    patched_globals = []
    for route in app.routes:
        endpoint = getattr(route, "endpoint", None)
        if endpoint is None:
            continue
        namespace = endpoint.__globals__
        if id(namespace) in patched_globals:
            continue
        if "OsirIpcCall" in namespace:
            monkeypatch.setitem(namespace, "OsirIpcCall", ipc)
            patched_globals.append(id(namespace))
        if "OsirSocket" in namespace:
            monkeypatch.setitem(namespace, "OsirSocket", FakeOsirSocket)
    return ipc


@pytest.fixture
def api(fake_ipc) -> TestClient:
    """FastAPI TestClient with the IPC backend stubbed out."""
    return TestClient(app)


@pytest.fixture
def bridge(monkeypatch, api):
    """Route the Python client's `requests` calls into the FastAPI TestClient.

    The client (osir_client) talks HTTP through `requests`; here each call is
    forwarded to the in-process API app, so client tests exercise the real
    routes, the real validation and the real response models.
    """
    import requests

    def fake_request(method, url, **kwargs):
        kwargs.pop("timeout", None)
        return api.request(method.upper(), urlparse(url).path, **kwargs)

    def fake_post(url, **kwargs):
        kwargs.pop("timeout", None)
        return api.post(urlparse(url).path, **kwargs)

    monkeypatch.setattr(requests, "request", fake_request)
    monkeypatch.setattr(requests, "post", fake_post)
    return api

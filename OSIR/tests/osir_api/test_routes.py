"""Route coverage for the whole OSIR API.

Every declared route is called through the FastAPI TestClient with a stubbed
IPC backend (see tests/conftest.py). This verifies, for each route:
- the path and method resolve (no 404),
- request validation accepts a well-formed input (no 422),
- the response validates against the declared response_model (no 500),
- the standardized envelope (version/status/message/response) is respected.

Routes that return a raw payload (files, download, tus) are asserted on their
own shape instead of the envelope.
"""
import pytest

CASE = "demo_case"
HANDLER = "11111111-1111-1111-1111-111111111111"
TASK = "22222222-2222-2222-2222-222222222222"
PROFILE = "demo_profile.yml"

ENVELOPE_KEYS = {"version", "status", "message", "response"}

# (id, method, path, kwargs for the TestClient call)
ROUTES = [
    ("active",          "get",     "/api/active", {}),
    ("version",         "get",     "/api/version", {}),
    ("metrics",         "get",     "/api/system/metrics", {"params": {"window_seconds": 60}}),
    ("case_list",       "get",     "/api/case", {}),
    ("case_create",     "post",    f"/api/case/{CASE}", {}),
    ("case_handlers",   "post",    f"/api/case/{CASE}/handler", {}),
    ("case_stats",      "get",     f"/api/case/{CASE}/stats", {}),
    ("case_tasks",      "get",     f"/api/case/{CASE}/tasks", {"params": {"page": 1, "page_size": 20}}),
    ("tasks_all",       "get",     "/api/tasks", {"params": {"page": 1}}),
    ("task_info",       "get",     f"/api/tasks/{TASK}/info", {}),
    ("task_restart",    "get",     f"/api/tasks/{TASK}/restart", {}),
    ("module_list",     "get",     "/api/module", {}),
    ("module_info",     "post",    "/api/module/info", {"json": {"modules": ["bodyfile.yml"]}}),
    ("profile_list",    "get",     "/api/profile", {}),
    ("profile_info",    "get",     f"/api/profile/{PROFILE}/info", {}),
    ("profile_run",     "post",    f"/api/profile/{PROFILE}/run", {"json": {"case_name": CASE}}),
    ("handler_create",  "post",    "/api/handler/create", {"json": {"case_name": CASE, "modules": ["bodyfile.yml"]}}),
    ("handler_advanced", "post",   "/api/handler/advanced", {"json": {"case_name": CASE, "files_modules": "bodyfile.yml", "files_input": [f"{CASE}://uploads/in.evtx"]}}),
    ("handler_delete",  "post",    "/api/handler/delete", {"json": {"handler_uuid": HANDLER}}),
    ("handler_info",    "post",    f"/api/handler/{HANDLER}/info", {}),
    ("handler_stats",   "post",    f"/api/handler/{HANDLER}/stats", {}),
    ("handler_task_info", "post",  f"/api/handler/{HANDLER}/task_info", {}),
    ("handler_tasks",   "get",     f"/api/handler/{HANDLER}/tasks", {"params": {"page": 1, "page_size": 20}}),
    ("handler_stop",    "post",    f"/api/handler/{HANDLER}/stop", {}),
    ("files_list",      "get",     "/api/files", {"params": {"path": f"{CASE}://"}}),
    ("files_delete",    "post",    "/api/files/delete", {"json": {"path": f"{CASE}://uploads", "items": [{"path": f"{CASE}://uploads/old.txt", "type": "file"}]}}),
    ("files_rename",    "post",    "/api/files/rename", {"json": {"path": f"{CASE}://uploads", "item": "old.txt", "name": "new.txt"}}),
    ("files_copy",      "post",    "/api/files/copy", {"json": {"path": f"{CASE}://uploads", "sources": [f"{CASE}://uploads/a.txt"], "destination": f"{CASE}://sub"}}),
    ("files_move",      "post",    "/api/files/move", {"json": {"path": f"{CASE}://uploads", "sources": [f"{CASE}://uploads/a.txt"], "destination": f"{CASE}://sub"}}),
    ("files_archive",   "post",    "/api/files/archive", {"json": {"path": f"{CASE}://uploads", "items": [{"path": f"{CASE}://uploads/a.txt", "type": "file"}], "name": "archive.zip"}}),
    ("files_unarchive", "post",    "/api/files/unarchive", {"json": {"path": f"{CASE}://uploads", "item": "archive.zip"}}),
    ("files_create_folder", "post", "/api/files/create-folder", {"json": {"path": f"{CASE}://uploads", "name": "subdir"}}),
    ("files_search",    "get",     "/api/files/search", {"params": {"path": f"{CASE}://", "filter": "*.txt", "deep": False}}),
    ("files_save",      "post",    "/api/files/save", {"json": {"path": f"{CASE}://uploads/note.txt", "content": "hello"}}),
    ("tus_options",     "options", "/api/files/upload", {}),
    ("tus_post",        "post",    "/api/files/upload", {"headers": {"Tus-Resumable": "1.0.0", "Upload-Length": "4"}, "content": b"data"}),
    ("tus_head",        "head",    "/api/files/upload/1234", {"headers": {"Tus-Resumable": "1.0.0"}}),
    ("tus_patch",       "patch",   "/api/files/upload/1234", {"headers": {"Tus-Resumable": "1.0.0", "Upload-Offset": "0"}, "content": b"data"}),
]

# Routes that return the raw payload (response_only=True), not the envelope
RAW_ROUTES = {"files_list", "files_delete", "files_rename", "files_copy", "files_move",
              "files_archive", "files_unarchive", "files_create_folder",
              "files_search", "files_save"}

# Routes with no JSON body (file download, tus handshake)
NO_BODY_ROUTES = {"tus_options", "tus_post", "tus_head", "tus_patch"}


@pytest.mark.parametrize("route_id,method,path,kwargs", ROUTES, ids=[r[0] for r in ROUTES])
def test_route(api, route_id, method, path, kwargs):
    response = api.request(method, path, **kwargs)
    assert response.status_code == 200, f"{method.upper()} {path}: {response.status_code} {response.text[:400]}"

    if route_id == "files_download":
        return  # handled by its own test below (binary response)

    if route_id in NO_BODY_ROUTES:
        return  # asserted by their own tests below

    body = response.json()
    if route_id in RAW_ROUTES:
        assert isinstance(body, dict), body
    else:
        assert ENVELOPE_KEYS <= set(body.keys()), body
        assert body["status"] == 200, body


# --- routes with a dedicated behavior --------------------------------------

def test_root_page(api):
    response = api.get("/")
    assert response.status_code == 200
    assert "OSIR API" in response.text


def test_files_download(api):
    response = api.get("/api/files/download", params={"path": "demo_case://uploads/hello.txt"})
    assert response.status_code == 200
    assert response.content == b"hello world"
    assert response.headers["content-type"].startswith("text/plain")
    assert "hello.txt" in response.headers.get("content-disposition", "")


def test_tus_options_headers(api):
    response = api.options("/api/files/upload")
    assert response.status_code == 200
    assert response.headers.get("tus-resumable") == "1.0.0"


def test_tus_post_location(api):
    response = api.post("/api/files/upload",
                        headers={"Tus-Resumable": "1.0.0", "Upload-Length": "4"},
                        content=b"data")
    assert response.status_code == 200
    assert response.headers.get("location") == "/api/files/upload/1234"


def test_tus_patch_offset(api):
    response = api.patch("/api/files/upload/1234",
                         headers={"Tus-Resumable": "1.0.0", "Upload-Offset": "0"},
                         content=b"data")
    assert response.status_code == 200
    assert response.headers.get("upload-offset") == "4"


def test_case_uploads_chunks(api):
    """Chunked multipart upload reassembles the file under CASES_DIR/<case>/uploads."""
    from osir_lib.core.OsirConstants import OSIR_PATHS

    api.post(f"/api/case/{CASE}")  # create the case directory first
    first = api.post(f"/api/case/{CASE}/uploads",
                     data={"name": "evidence.txt", "chunk_number": 0, "total_chunks": 2},
                     files={"file": ("evidence.txt", b"part1-", "application/octet-stream")})
    assert first.status_code == 200
    assert first.json()["message"] == "Chunk Uploaded"

    last = api.post(f"/api/case/{CASE}/uploads",
                   data={"name": "evidence.txt", "chunk_number": 1, "total_chunks": 2},
                   files={"file": ("evidence.txt", b"part2", "application/octet-stream")})
    assert last.status_code == 200
    assert last.json()["message"] == "File Uploaded"

    uploaded = OSIR_PATHS.CASES_DIR / CASE / "uploads" / "evidence.txt"
    assert uploaded.exists()
    assert uploaded.read_bytes() == b"part1-part2"


def test_profile_info_not_found(api):
    response = api.get("/api/profile/does_not_exist.yml/info")
    assert response.status_code == 200
    body = response.json()
    assert body["response"] is None
    assert "not found" in body["message"].lower()


# --- contract negatives ----------------------------------------------------

def test_unknown_route_is_404(api):
    assert api.get("/api/does_not_exist").status_code == 404


def test_files_list_requires_path(api):
    assert api.get("/api/files").status_code == 422


def test_handler_create_requires_case_name(api):
    response = api.post("/api/handler/create", json={"modules": ["bodyfile.yml"]})
    assert response.status_code == 422


def test_route_count_matches_expectations(api):
    """Every API route declared by the app is covered by this module.

    The parametrized ROUTES cover most of them; files_download and the chunked
    upload have dedicated tests and are counted in here.
    """
    covered = {(m.upper(), p) for _, m, p, _ in ROUTES}
    covered |= {("GET", "/api/files/download"), ("POST", f"/api/case/{CASE}/uploads")}
    declared = {
        (sorted(r.methods)[0], r.path)
        for r in api.app.routes
        if hasattr(r, "methods") and r.path.startswith("/api")
    }
    formatted = set()
    for method, path in declared:
        formatted.add((method, path
                      .replace("{case_name}", CASE)
                      .replace("{profile_name}", PROFILE)
                      .replace("{handler_id}", HANDLER)
                      .replace("{task_id}", TASK)
                      .replace("{uuid}", "1234")))
    missing = formatted - covered
    assert not missing, f"routes declared but not covered by ROUTES: {missing}"

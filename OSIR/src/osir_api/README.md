# OSIR API

FastAPI-based REST API for the OSIR DFIR framework. Every endpoint is a thin wrapper: it validates the request with Pydantic, forwards it to the `osir_service` backend over IPC (`OsirIpcCall`), and returns a standardized JSON response. Routers in `api/` are auto-discovered and mounted under `/api` (see `OsirApi.py`).

## Run

```bash
uvicorn osir_api.OsirApi:app --host 0.0.0.0 --port 8000
```

Interactive documentation: Swagger UI at `/docs`, ReDoc at `/redoc`, OpenAPI spec at `/openapi.json`.

## Endpoints

All endpoints are prefixed with `/api`.

### Cases

| Method | Path | Description |
|--------|------|-------------|
| GET | `/case` | List all cases |
| POST | `/case/{case_name}` | Create a case |
| POST | `/case/{case_name}/handler` | List the handlers of a case |
| GET | `/case/{case_name}/stats` | Task statistics for a case |
| GET | `/case/{case_name}/tasks` | List the tasks of a case |
| POST | `/case/{case_name}/uploads` | Upload a file chunk to a case |

### Modules

| Method | Path | Description |
|--------|------|-------------|
| GET | `/module` | List available modules |
| POST | `/module/info` | Get module configuration (module names in the body) |

### Profiles

| Method | Path | Description |
|--------|------|-------------|
| GET | `/profile` | List available profiles |
| GET | `/profile/{profile_name}/info` | Get a profile definition |
| POST | `/profile/{profile_name}/run` | Run a profile on a case |

### Handlers

| Method | Path | Description |
|--------|------|-------------|
| POST | `/handler/create` | Create a handler from a profile and/or modules |
| POST | `/handler/advanced` | Run modules directly on files/folders (no watchdog) |
| POST | `/handler/delete` | Delete a handler and its tasks |
| POST | `/handler/{handler_id}/info` | Get handler status |
| POST | `/handler/{handler_id}/stats` | Task statistics for a handler |
| POST | `/handler/{handler_id}/task_info` | All task logs of a handler |
| GET | `/handler/{handler_id}/tasks` | Paginated tasks of a handler (filters: `status`, `module`, `input`) |
| POST | `/handler/{handler_id}/stop` | Stop a running handler |

### Tasks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/tasks` | List tasks |
| GET | `/tasks/{task_id}/info` | Get a task record |
| GET | `/tasks/{task_id}/restart` | Re-submit a task |

### Files

| Method | Path | Description |
|--------|------|-------------|
| GET | `/files` | List files and folders |
| GET | `/files/download` | Download a file |
| GET | `/files/search` | Search files by name |
| POST | `/files/delete`, `/files/rename`, `/files/copy`, `/files/move`, `/files/archive`, `/files/unarchive`, `/files/create-folder`, `/files/save` | File operations (JSON body) |

### Uploads (tus resumable protocol)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/files/upload` | Create an upload session |
| PATCH | `/files/upload/{uuid}` | Send a chunk to an upload session |

### Monitoring

| Method | Path | Description |
|--------|------|-------------|
| GET | `/active` | Check the OSIR service is up |
| GET | `/version` | API version |
| GET | `/system/metrics` | Recent host resource samples |

## Examples

```bash
# Create a case
curl -X POST "http://localhost:8000/api/case/MyCase"

# Run a module on it
curl -X POST "http://localhost:8000/api/handler/create" \
  -H "Content-Type: application/json" \
  -d '{"case_name": "MyCase", "modules": ["bodyfile.yml"]}'

# Follow the resulting handler
curl -X POST "http://localhost:8000/api/handler/<handler_id>/info"
```

## Response Format

All responses share the same envelope:

```json
{
  "version": "1.1",
  "status": 200,
  "message": "Everything is working as it should!",
  "response": { "...": "..." }
}
```

On error, `response` contains an `error` key with the detailed message.

## Architecture

- `OsirApi.py` — FastAPI app (CORS, exception handlers); auto-discovers every `api/*.py` exposing a `router` and mounts it under `/api`
- `api/OsirApi<Domain>.py` — one router per domain (Case, Module, Profile, Handler, Task, Files, Tus, Monitoring, Status, Version)
- `api/OsirIpcCall.py` — forwards each endpoint call to `osir_service` over IPC
- `api/model/` — Pydantic request/response models

## Dependencies

FastAPI, Uvicorn, Pydantic, `osir-lib`, `osir-service` (IPC backend).

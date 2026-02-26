# FastAPI API - OSIR API

## Overview

OSIR API is a **FastAPI**-based API designed for digital forensics and incident response (DFIR) operations. It provides a structured interface for executing OSIR modules, managing cases, profiles, and monitoring investigation status.

## Features

- **FastAPI Powered**: Modern, high-performance API with automatic OpenAPI/Swagger documentation
- **Case Management**: Create, retrieve, and manage forensic cases
- **Module Execution**: Run individual forensic modules on demand
- **Profile Execution**: Execute predefined investigation profiles
- **Status Execution**: Track active handlers and tasks

## Installation

### Prerequisites

- Python 3.7+
- FastAPI
- Pydantic
- Required OSIR dependencies

## Quick Start

```bash
# Start the FastAPI server
uvicorn osir_api.main:app --reload

# Access the interactive API documentation
http://localhost:8000/docs

# Access the API endpoints
http://localhost:8000/api
```

## API Endpoints

### Base URL
`/api` - All endpoints are prefixed with `/api`

### Case Management

- **GET** `/case` - List all available cases
- **POST** `/case/{case_name}` - Create a new case
- **POST** `/case/{case_name}/handler` - Get handlers for a specific case

### Module Operations

- **GET** `/module` - List all available modules (structured by category)
- **GET** `/module/{module_name}/info` - Get information about a specific module
- **POST** `/module/{module_name}/run` - Execute a specific module

### Profile Operations

- **GET** `/profile` - List all available profiles
- **GET** `/profile/{profile_name}/info` - Get information about a specific profile
- **POST** `/profile/{profile_name}/run` - Execute a profile

### Handler Operations

- **POST** `/handler/{handler_uuid}/info` - Get status of a specific handler

### Task Operations

- **GET** `/tasks` - List all tasks
- **GET** `/tasks/{task_id}/info` - Get information about a specific task

### Status Monitoring

- **GET** `/active` - Check if OSIR service is active

### Version

- **GET** `/version` - Get API version information

## API Usage Examples

### Create a Case

```bash
curl -X POST "http://localhost:8000/api/case/MyCaseName" \
  -H "Content-Type: application/json"
```

### List Available Modules

```bash
curl -X GET "http://localhost:8000/api/module"
```

### Get Module Information

```bash
curl -X GET "http://localhost:8000/api/module/disk_analysis/info"
```

### Run a Module

```bash
curl -X POST "http://localhost:8000/api/module/disk_analysis/run" \
  -H "Content-Type: application/json" \
  -d '{"case_name": "Phishing-Incident-001"}'
```

### List Available Profiles

```bash
curl -X GET "http://localhost:8000/api/profile"
```

### Get Profile Information

```bash
curl -X GET "http://localhost:8000/api/profile/uac/info"
```

### Run a Profile

```bash
curl -X POST "http://localhost:8000/api/profile/uac/run" \
  -H "Content-Type: application/json" \
  -d '{"case_name": "Phishing-Incident-001"}'
```

### Check Handler Status

```bash
curl -X POST "http://localhost:8000/api/handler/a1b2c3d4-e5f6-7890-abcd-ef1234567890/info" \
  -H "Content-Type: application/json"
```

### List Tasks

```bash
curl -X GET "http://localhost:8000/api/tasks"
```

### Get Task Information

```bash
curl -X GET "http://localhost:8000/api/tasks/task123/info"
```

## Response Format

All responses follow a consistent structure:

```json
{
  "version": "1.1",
  "status": 200,
  "message": "Everything is working as it should!",
  "response": {
    "data": "..."
  }
}
```

## Error Handling

The API provides detailed error responses:

```json
{
  "version": "1.1",
  "status": 500,
  "response": {
    "error": "UNEXPECTED ERROR: Detailed error message"
  }
}
```

## Interactive Documentation

The API includes automatic OpenAPI documentation:

- **Swagger UI**: `/docs` - Interactive API exploration and testing
- **ReDoc**: `/redoc` - Alternative documentation format
- **OpenAPI JSON**: `/openapi.json` - Machine-readable API specification

## Architecture

### Core Components

- **FastAPI Application**: Main web server with automatic documentation
- **API Routers**: Modular endpoint organization
- **Pydantic Models**: Request/response validation and serialization
- **IPC Client**: Communication with OSIR backend services
- **File Manager**: Case and module file system operations

### Key Files

- `OsirApi.py` - FastAPI application setup and router registration
- `api/OsirApiCase.py` - Case management endpoints
- `api/OsirApiModule.py` - Module execution endpoints
- `api/OsirApiProfile.py` - Profile management endpoints
- `api/OsirApiHandler.py` - Handler status endpoints
- `api/OsirApiTask.py` - Task management endpoints
- `api/OsirApiStatus.py` - Service health checks
- `api/OsirApiVersion.py` - API version information


## Configuration

Environment variables can be used to configure the API:

```bash
# Example environment variables
export OSIR_API_HOST=0.0.0.0
export OSIR_API_PORT=8000
```

## Dependencies

- FastAPI
- Pydantic
- Uvicorn (ASGI server)
- osir-lib (core OSIR library)
- osir-service (IPC communication)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or feature requests:
- Open an issue on the GitHub repository
- Check the interactive API documentation at `/docs`
- Review the automatic OpenAPI specification at `/openapi.json`

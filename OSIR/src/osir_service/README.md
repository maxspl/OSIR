# OSIR Service Package

The `osir_service` package provides the core service infrastructure for the OSIR (Open Source Incident Response) framework. It handles task orchestration, inter-process communication, database management, and distributed processing.

## Overview

OSIR Service is a distributed forensic analysis framework that uses:
- **Celery** for distributed task processing
- **PostgreSQL** for case and task management
- **RabbitMQ** for message brokering
- **Redis** for result backend
- **Custom IPC** for inter-process communication

## Package Structure

```
osir_service/
├── agent/                  # Agent management and worker services
├── ipc/                    # Inter-process communication services
├── orchestration/          # Task orchestration and processing
├── postgres/               # Database models and services
├── smb/                    # SMB/CIFS network services
└── watchdog/               # File system monitoring services
```

## Core Components

### 1. Agent Service (`agent/AgentService.py`)

The `CeleryWorker` class manages distributed forensic task execution:

**Key Features:**
- Manages multiple Celery worker queues for different OS types (Windows/Unix)
- Handles task lifecycle: submission, execution, monitoring, and result collection
- Supports both internal (Python) and external (binary) module execution

**Worker Types:**
- `unix_worker_no_multithread`: Single-threaded Unix workers
- `unix_worker_multithread`: Multi-threaded Unix workers  
- `windows_worker_no_multithread`: Single-threaded Windows workers
- `windows_worker_multithread`: Multi-threaded Windows workers
- `*_disk_only`: Workers for disk-intensive operations (standalone mode only)

### 2. IPC Service (`ipc/IpcService.py`)

The `IpcService` class provides JSON-based inter-process communication:

**Supported Actions:**
- `socket_on`: Test connection readiness
- `exec_module`: Execute a single forensic module
- `exec_profile`: Execute a module profile
- `create_case`: Create a new forensic case
- `get_cases`: List all cases
- `get_tasks`: Get tasks for a specific case
- `get_task_log`: Retrieve logs for a specific task
- `get_handler_status`: Check handler execution status
- `get_case_handler`: Get handlers for a case

**Usage:**
```python
from osir_service.ipc.IpcService import IpcService

ipc = IpcService(host="localhost", port=5000)
ipc.start()  # Starts listener in background thread
```

### 3. Task Service (`orchestration/TaskService.py`)

The `TaskService` class handles task submission to the Celery cluster:

**Key Methods:**
- `push_task()`: Submit a task to the appropriate queue
- `get_task_name()`: Determine task type (internal/external)
- `get_queue_name()`: Determine appropriate queue based on module requirements

**Task Routing:**
Tasks are automatically routed to the appropriate queue based on:
- Processor OS (Windows/Unix)
- Multithreading capability
- Disk-only operations
- Module type (internal/external)

### 4. Database Service (`postgres/OsirDb.py`)

The `OsirDb` class provides PostgreSQL database access:

**Database Tables:**
- **Cases**: Forensic case metadata
- **Handlers**: Execution handlers for module batches
- **Tasks**: Individual task execution records
- **Snapshots**: System state snapshots

**Key Features:**
- Automatic connection management with retry logic
- Context manager support (`with OsirDb() as db:`)
- Table creation and schema management
- Transaction support

## Usage Examples

### Starting the Agent

```python
from osir_service.agent.AgentService import CeleryWorker

worker = CeleryWorker()
worker.start_worker()  # Starts all worker processes
```

### Submitting a Task

```python
from osir_service.orchestration.TaskService import TaskService
from osir_lib.core.model.OsirModuleModel import OsirModuleModel

# Create module instance
module = OsirModuleModel.from_name("evtx_extract")
module.input.match = "/path/to/evtx/file"

# Submit task
task_id = TaskService.push_task(
    case_path="/cases/my_case",
    module_instance=module,
    case_uuid="case-uuid-here"
)
```

### Using IPC Service

```python
from osir_service.ipc.IpcService import IpcService
from osir_service.ipc.OsirIpc import OsirIpc

# Create IPC service
ipc = IpcService(host="localhost", port=5000)
ipc.start()

# Create request
request = OsirIpc(
    action="exec_module",
    case_path="/cases/my_case",
    modules=["evtx_extract"]
)

# Send request and get response
response = ipc.action(request.model_dump())
```
# OSIR Service Package

The `osir_service` package provides the core service infrastructure for the OSIR framework. It handles task orchestration, inter-process communication, database management, and distributed processing.

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
├── ipc/                    # Inter-process communication services and processing
├── orchestration/          # Task orchestration
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

### 2. IPC Service (`ipc/OsirIpc.py`)

The `OsirIpc` class provides JSON-based inter-process communication, covering all actions available through the OSIR API and Web interfaces. It handles every call and process of the OSIR project. It listens on a TCP socket and dispatches JSON requests to registered action handlers.

**Supported Actions:**

*Connection:*
- `socket_on`: Test connection readiness

*Execution:*
- `exec_module`: Execute a single forensic module on a case or a specific input file
- `exec_profile`: Execute a module profile
- `restart_task`: Re-submit a task by its ID
- `stop_handler`: Stop a running handler

*Handlers:*
- `create_handler`: Create a handler with profile/modules validation and start processing
- `create_advanced_handler`: Run modules directly on specific files or folders (no watchdog)
- `delete_handler`: Delete a handler and its tasks
- `get_handler_status`: Check handler execution status
- `get_case_handler`: Get handlers for a case
- `get_handler_task_info`: Retrieve all task logs for a handler
- `get_system_metrics`: Get recent host resource samples (per agent) for the web UI graphs

*Cases:*
- `create_case`: Create a new forensic case
- `get_cases`: List all cases

*Tasks:*
- `get_tasks`: Get tasks with filtering (case, handler, module, status) and pagination
- `get_task_stats`: Get aggregated task statistics for a case or handler
- `get_task_log`: Retrieve logs for a specific task

*Modules:*
- `get_modules`: List all available modules
- `get_module_info`: Get configuration details for specific modules

*File management:*
- `files_list`: List files and folders
- `files_delete`: Delete files or folders
- `files_rename`: Rename files or folders
- `files_copy`: Copy files or folders
- `files_move`: Move files or folders
- `files_archive`: Archive files or folders
- `files_unarchive`: Extract archives
- `files_create_folder`: Create a folder
- `files_download`: Download a file
- `files_search`: Search files by name

*Upload (tus protocol):*
- `tus_upload_options`: Handle tus preflight (OPTIONS) requests
- `tus_upload_post`: Create a tus upload session
- `tus_upload_patch`: Send a chunk of data to an upload session
- `tus_upload_head`: Get upload session status

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
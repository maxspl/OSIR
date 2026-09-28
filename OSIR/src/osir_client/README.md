# OSIR Client

A Python client for interacting with the OSIR API, designed to manage forensic cases, run modules, and handle digital investigation workflows.

## Installation

### Prerequisites
- Python 3.8+
- OSIR API server running (default: `http://127.0.0.1:8502`)

### Install from source

```bash
# Clone the repository
git clone https://github.com/maxspl/OSIR.git
cd OSIR/src/osir_client

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install .
```

## Concepts

The client mirrors the OSIR workflow. You connect through an `OsirClient`, and everything starts from **cases**. Each case gives access to its **modules**, **profiles**, **handlers** and **tasks**. Running a module or a profile returns a **handler**, which represents one processing batch on that case.

```
OsirClient (api_url)
└── client.cases           → create / get / list cases
    └── case (OsirCliCase)
        ├── case.modules   → run a single module          → returns a Handler
        ├── case.profiles  → run a profile (module set)   → returns a Handler
        ├── case.handlers  → list handlers, follow status
        └── case.tasks    → list tasks, inspect one by ID
```

Most `list()` and `status()` calls print a formatted table to the console (via `rich`); pass `print=False` where supported to get the raw data instead.

## Quick Start

```python
from osir_client.client.OsirClient import OsirClient

# Connect to the OSIR API
client = OsirClient(api_url="http://127.0.0.1:8502")
client.is_active()  # True if the server responds

# Create a new case (or fetch an existing one)
case = client.cases.create("my_forensic_case")
# case = client.cases.get("my_forensic_case")

# Run a module on the case — returns a Handler
handler = case.modules.run("bodyfile.yml")

# Wait until the handler finishes (done or failed), polling every 5s
handler.status(wait_end=True)  # default timeout: 300s

# Inspect the results
case.tasks.list()                              # print all tasks of the case
task = case.tasks.get_task_info("<task_id>")   # full record of one task
```

## API Reference

### OsirClient

Entry point for all calls. Requires the URL of the OSIR API server.

```python
from osir_client.client.OsirClient import OsirClient

client = OsirClient(api_url="http://127.0.0.1:8502")
client.is_active()  # check the server is reachable
```

### Cases

`client.cases` is the entry point for case management. `create()` and `get()` return the case object used to access modules, profiles, handlers and tasks.

```python
# Create a new case (returns a case with name and case_uuid set)
case = client.cases.create("case_name")

# Get an existing case by name
case = client.cases.get("case_name")

# Print the list of all cases
client.cases.list()
```

### Modules

`case.modules` runs forensic modules.

```python
# List available modules (prints a table and returns the module paths)
modules = case.modules.list()

# Get a module's configuration (returns None if it does not exist)
module = case.modules.exists("module_name.yml")

# Run a module on the case — returns a Handler
handler = case.modules.run("module_name.yml")

# Run a module on a local file — the file is uploaded to the case first
handler = case.modules.run("module_name.yml", "/path/to/input/file")
```

The upload in the last example is automatic and chunked (10 MB per chunk); you never call the upload endpoint directly.

### Profiles

`case.profiles` runs predefined module sets (profiles).

```python
# List available profiles (prints a table and returns the profile paths)
profiles = case.profiles.list()

# Get a profile's definition (returns None if it does not exist)
profile = case.profiles.exists("profile_name.yml")

# Run a profile on the case — returns a Handler
handler = case.profiles.run("profile_name.yml")
```

### Handlers

A handler is one processing batch: a single module run, or all the modules of a profile. `run()` calls return it, and its `handler_id` is the key used by the server.

```python
# List all handlers of the case
case.handlers.list()

# Print the current status of a handler
handler.status()

# Wait until the handler completes or fails
handler.status(wait_end=True)                  # timeout=300s, poll every interval=5s
handler.status(wait_end=True, timeout=600, interval=10)
```

A handler's life cycle is: `processing_started` → `processing_done` or `processing_failed`. With `wait_end=True`, `status()` raises a `TimeoutError` if the handler does not finish within `timeout` seconds.

### Tasks

`case.tasks` inspects individual task executions.

```python
# Print all tasks of the case
case.tasks.list()

# Get a task by its ID (prints a table and returns the task record)
task = case.tasks.get_task_info("task_id")

# Get the record without printing
task = case.tasks.get_task_info("task_id", print=False)
```

### Environment Variables

Create a `.env` file:

```env
OSIR_API_URL="http://127.0.0.1:8502"
```

## Dependencies

The package requires:

- `requests`: For HTTP communication
- `pydantic`: For data validation and models
- `rich`: For enhanced console output
- `tabulate`: For table formatting
- `python-dotenv`: For environment variable management

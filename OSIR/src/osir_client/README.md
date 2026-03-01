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

## Quick Start

### Basic Usage

```python
from osir_client.client.OsirClient import OsirClient

# Initialize the client
api_url = "http://127.0.0.1:8502"
osir_client = OsirClient(api_url=api_url)

# Create a new case
case = osir_client.cases.create("my_forensic_case")

# Run a module on the case
handler = case.modules.run("bodyfile.yml")

# Wait for processing to complete
handler.status(wait_end=True)

# Get task information
first_task = handler.tasks.list().select(0)
first_task.status()
first_task.log()
```

## Features

### Case Management
- Create, list, and manage forensic cases
- Access case information and metadata
- Case lifecycle management

### Module Execution
- Run forensic modules against cases
- Upload files for analysis
- Monitor module execution status
- Retrieve module results and logs

### Profile Management
- Execute predefined investigation profiles
- Automate complex workflows
- Profile-based analysis

### Task Monitoring
- Track task execution status
- View task logs and outputs
- Manage task lifecycle

## API Reference

### OsirClient

The main client class for connecting to the OSIR API.

```python
from osir_client.client.OsirClient import OsirClient

client = OsirClient(api_url="http://127.0.0.1:8502")
```

### Cases

Manage forensic cases:

```python
# Create a new case
case = client.cases.create("case_name")

# Get a specific case
case = client.cases.get("case_name")

# List all cases
cases = client.cases.list()
```

### Modules

Execute forensic modules:

```python
# Run a module on a case
handler = case.modules.run("module_name.yml")

# Run a module with input file
handler = case.modules.run("module_name.yml", "/path/to/input/file")

# Check if module exists
module_info = case.modules.exists("module_name.yml")

# List available modules
modules = case.modules.list()
```

### Profiles

Execute investigation profiles:

```python
# Run a profile on a case
handler = case.profiles.run("profile_name.yml")

# List available profiles
profiles = case.profiles.list()
```

### Handlers

Manage module execution:

```python
# Check handler status
handler.status(wait_end=True)  # Wait for completion
handler.status()  # Get current status

# Access tasks
tasks = handler.tasks.list()
first_task = tasks.select(0)

# Get task information
first_task.status()
first_task.log()
```

## Configuration

The client can be configured using environment variables or directly in code.

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

## Support

For issues, questions, or contributions, please visit the [OSIR GitHub repository](https://github.com/maxspl/OSIR).
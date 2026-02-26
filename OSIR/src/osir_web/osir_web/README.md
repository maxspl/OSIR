# OSIR Web Interface

A Streamlit-based web application for managing and monitoring forensic processing tasks in the OSIR framework.

## Overview

The OSIR Web Interface provides a user-friendly way to configure, launch, and monitor forensic processing jobs. It's designed for digital forensics professionals to efficiently process cases using various processing modules.

## Features

### Main Functionality
- **Profile/Module Management**: Select predefined profiles or individual modules for processing
- **In-Memory Configuration**: Edit module configurations without modifying underlying YAML files
- **Case Processing**: Launch processing jobs on specific cases (directories of files)
- **Real-time Monitoring**: Track worker status and task progress

### Key Pages

1. **Processor (Main Page)**
   - Select profiles or individual modules
   - Edit module configurations in a code editor
   - Launch processing jobs on selected cases
   - Three main tabs: Main, Apply Module, and Helper

2. **Master Agent Status**
   - Monitor running Celery workers via Flower API
   - View detailed task information
   - System resource monitoring

3. **Processing Status**
   - View handlers and tasks by case
   - Filter tasks by status, handler ID, or module
   - View detailed task logs and execution traces
   - Database cleanup functionality

## Installation

### Prerequisites
- Python 3.8+
- Docker (for full OSIR framework)
- PostgreSQL
- Celery + Flower for task monitoring

### Setup

```bash
# Clone the OSIR repository
git clone https://github.com/maxspl/OSIR.git
cd OSIR/src/osir_web

# Install dependencies
pip install -r requirements.txt

# Run the web interface
streamlit run Processor.py
```

## Configuration

The application uses a `config.toml` file for basic settings:

```toml
[theme]
base="light"
```

## Usage

### Starting the Application

```bash
streamlit run Processor.py
```

The application will be available at `http://localhost:8501` by default.

### Basic Workflow

1. **Select Profile/Modules**: Choose a predefined profile or individual modules
2. **Configure Modules**: Optionally edit module configurations in the code editor
3. **Select Case**: Choose the case directory to process
4. **Launch Job**: Click Submit to start processing
5. **Monitor Progress**: Use the Processing Status page to track job progress

### Applying Single Modules

1. Navigate to the "Apply Module" tab
2. Select a case and specific file
3. Choose a module to apply
4. Optionally edit the module configuration
5. Click Submit to process the file

## Architecture

```
┌───────────────────────────────────────────────────┐
│                 OSIR Web Interface                 │
├───────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────────┐          │
│  │  Processor  │    │ MasterAgentStatus │         │
│  │  (Main App) │    │ (Worker Monitor) │         │
│  └─────────────┘    └─────────────────┘          │
│  ┌─────────────────────────────────────────────┐  │
│  │           ProcessingStatus                │  │
│  │  (Task Monitoring & Management)           │  │
│  └─────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────┘
                    │              │
                    ▼              ▼
┌─────────────────────────┐  ┌─────────────────┐
│   PostgreSQL Database   │  │  Celery Workers  │
│  (Task & Handler Data)  │  │  (Processing)    │
└─────────────────────────┘  └─────────────────┘
```

## Key Components

### Processor.py

The main application class `ConfigurationApp` handles:
- Profile and module discovery
- In-memory configuration editing
- Job submission and processing
- User interface rendering

### MasterSideBar.py

Provides system monitoring and navigation:
- Host specifications (CPU, RAM, disk)
- Case usage statistics
- Useful links to database and Splunk

### Database Schema

The application interacts with several database tables:
- `case`: Case information
- `handler`: Processing handlers
- `task`: Individual processing tasks
- `master_status`: System status

## Development

### Running Tests

```bash
# Run unit tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=osir_web tests/
```

### Building Documentation

```bash
# Build Sphinx documentation
cd docs
make html
```

## Troubleshooting

### Common Issues

1. **Database connection errors**: Verify PostgreSQL is running and credentials are correct
2. **Worker not showing**: Check Celery and Flower services are running
3. **Module loading errors**: Ensure module YAML files are properly formatted

### Debugging

Enable debug logging by setting the environment variable:

```bash
export OSIR_LOG_LEVEL=DEBUG
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: https://github.com/maxspl/OSIR/issues
- Documentation: https://github.com/maxspl/OSIR

## Roadmap

Future enhancements planned:
- Advanced task scheduling
- User authentication and RBAC
- Enhanced reporting features
- API endpoints for integration

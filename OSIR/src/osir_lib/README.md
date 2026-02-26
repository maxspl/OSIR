# OSIR Library

This library is the core of OSIR. It provides all the classes and functions used across the other OSIR packages.


## Installation

```bash
# Clone the repository
git clone https://github.com/maxspl/OSIR.git


# Install the package
pip install -e OSRIR_PATHS/osir_lib
```

## Quick Start

### Basic Usage

```python
from osir_lib.core.OsirModule import OsirModule
from osir_lib.core.model.OsirModuleModel import OsirModuleModel

# Load MFT module
mft_module = OsirModuleModel.from_name("mft")
mft_module.input.match = "/cases/incident_001/evidence/$MFT"

# Configure
osir_mft = OsirModule(**mft_module.model_dump())
osir_mft.case_path = "/cases/incident_001"

# Run processing
success = osir_mft.tool.run()
if success:
    print(f"MFT processed successfully. Output: {osir_mft.output.output_file}")
```

## Configuration

### Environment Variables

- `OSIR_HOME`: Set the base directory for OSIR (default: `/OSIR`)
- `LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)

## Contributing

Contributions are welcome! Please submit pull requests or open issues for bugs and feature requests.

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.
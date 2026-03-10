import os
import pytest
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_lib.core.FileManager import FileManager

def test_structure_all_modules():
    assert "OSIR_PATH" in os.environ, "OSIR_PATH environment variable is not set"
    try:
        for module_name in FileManager.all_modules():
            OsirModuleModel.from_name(module_name)
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")
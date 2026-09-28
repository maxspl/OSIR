"""Validate the structure of every deployed module YAML.

Requires a deployed OSIR environment (the OSIR_PATH environment variable);
skipped automatically otherwise so the local suite stays green.
"""
import os

import pytest

from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_lib.core.FileManager import FileManager

pytestmark = pytest.mark.skipif(
    not os.environ.get("OSIR_PATH"),
    reason="OSIR_PATH not set — requires a deployed OSIR environment",
)


def test_structure_all_modules():
    try:
        for module_name in FileManager.all_modules():
            OsirModuleModel.from_name(module_name)
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")
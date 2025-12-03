import importlib
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from osir_api.api.exceptions import (
    ModuleNotFoundException,
    ModuleValidationException,
    ModuleLoadException,
    UnexpectedException,
    module_not_found_handler,
    module_validation_handler,
    module_load_handler,
    unexpected_error_handler
)

MODULES_DIR = "/OSIR/OSIR/configs/modules/network"

app = FastAPI(
    title="OSIR API",
    description="API pour exécuter des modules OSIR",
    version="1.0.0"
)

# Register exception handlers
app.add_exception_handler(ModuleNotFoundException, module_not_found_handler)
app.add_exception_handler(ModuleValidationException, module_validation_handler)
app.add_exception_handler(ModuleLoadException, module_load_handler)
app.add_exception_handler(UnexpectedException, unexpected_error_handler)


API_FOLDER = Path(__file__).parent / "api"
ROUTE_PREFIX = "/api"

for file in API_FOLDER.glob("*.py"):
    if file.name == "__init__.py":
        continue
    module_name = f"api.{file.stem}"
    
    spec = importlib.util.spec_from_file_location(module_name, file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    if hasattr(mod, "router"):
        app.include_router(mod.router, prefix=ROUTE_PREFIX)


# @app.get("/modules")
# def get_modules():
#     """Liste les modules OSIR disponibles"""
#     try:
#         if not os.path.isdir(MODULES_DIR):
#             raise Exception(f"Modules directory not found: {MODULES_DIR}")
#         return [f for f in os.listdir(MODULES_DIR) if f.endswith(".yml")]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
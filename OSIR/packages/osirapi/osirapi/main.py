import importlib
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODULES_DIR = "/OSIR/OSIR/configs/modules/network"

app = FastAPI(
    title="OSIR API",
    description="API pour exécuter des modules OSIR",
    version="1.0.0"
)

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
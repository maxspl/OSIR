import importlib
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from osir_api.api.OsirApiExceptions import (
    UnexpectedException,
    unexpected_error_handler
)

app = FastAPI(
    title="OSIR API",
    description="OSIR API",
    version="1.0"
)

app.add_exception_handler(UnexpectedException, unexpected_error_handler)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """
    Default home page of the OSIR API.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OSIR API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f4f9;
                color: #333;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                text-align: center;
            }
            .container {
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                padding: 30px;
                max-width: 600px;
                width: 90%;
            }
            h1 {
                color: #2c3e50;
                margin-bottom: 20px;
            }
            p {
                margin-bottom: 15px;
                line-height: 1.6;
            }
            a {
                color: #3498db;
                text-decoration: none;
                font-weight: bold;
            }
            a:hover {
                text-decoration: underline;
            }
            .footer {
                margin-top: 20px;
                font-size: 0.9em;
                color: #7f8c8d;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to the OSIR API</h1>
            <p>This API allows you to execute and manage OSIR modules.</p>
            <p>Check out the <a href="/docs">interactive documentation</a> to explore available endpoints.</p>
            <p>Or access the endpoints directly under <a href="/api">/api</a>.</p>
            <div class="footer">
                <p>© 2025 OSIR API</p>
            </div>
        </div>
    </body>
    </html>
    """

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

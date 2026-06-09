# from enum import Enum
import base64

from fastapi import FastAPI, Header, Request, HTTPException, params
# from fastapi.routing import APIRoute, APIRouter
# from starlette.requests import ClientDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
# from typing import Annotated, Union, Any, Hashable
# import base64
# import hashlib
# from uuid import uuid4
# from datetime import datetime, timedelta
# import os

# from typing import Dict, List, Optional, Union, Sequence

# from .filestore import FileInfo, FileStore


from fastapi import APIRouter

from osir_api.api.model.OsirApiTaskModel import GetTaskInfoResponse
from osir_api.api.OsirApiExceptions import UnexpectedExceptionResponse
from osir_api.api.OsirIpcCall import OsirIpcCall
from fastapi import status
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

router = APIRouter()

@router.options("/files/upload")
def read_server_config(request: Request) -> Response:
    return OsirIpcCall("tus_upload_options")


@router.post("/files/upload")
async def post_file(
    request: Request,
    response: Response,
    upload_metadata: str = Header(None),
    upload_length: int = Header(None),
    upload_defer_length: int = Header(None),
    content_length: int = Header(None),
    content_type: str = Header(None),
):
    # Read the body as bytes
    body_bytes = await request.body()

    # Encode the body in base64 for JSON serialization
    body_encoded = base64.b64encode(body_bytes).decode("utf-8")

    return OsirIpcCall(
        "tus_upload_post",
        params={
            "req": body_encoded,
            "upload_metadata": upload_metadata,
            "upload_length": upload_length,
            "upload_defer_length": upload_defer_length,
            "content_length": content_length,
            "content_type": content_type,
        }
    )

@router.patch("/files/upload/{uuid}")
async def patch_file(
    request: Request,
    response: Response,
    uuid: str,
    tus_resumable: str = Header(None),
    content_length: int = Header(None),
    content_type: str = Header(None),
    upload_offset: int = Header(None),
    upload_length: int = Header(None),
):
    # Read the body as bytes
    body_bytes = await request.body()

    # Encode the body in base64 for JSON serialization
    body_encoded = base64.b64encode(body_bytes).decode("utf-8")

    return OsirIpcCall(
        "tus_upload_patch",
        params={
            "req": body_encoded,
            "uuid": uuid,
            "tus_resumable": tus_resumable,
            "content_length": content_length,
            "content_type": content_type,
            "upload_offset": upload_offset,
            "upload_length": upload_length,
        }
    )
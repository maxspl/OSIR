import base64
from fastapi import Header, Request
from fastapi.responses import JSONResponse, Response
from fastapi import APIRouter

from osir_api.api.OsirIpcCall import OsirIpcCall, OsirIpcRequest, OsirIpcResponse, OsirSocket, handle_response
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
    body_bytes = await request.body()
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

@router.head("/files/upload/{uuid}")
async def upload_head(uuid: str):
    return OsirIpcCall(
        "tus_upload_head", 
        params={
            "uuid": uuid
        })

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
    last_call = None
    with OsirSocket() as client:
        async for chunk in request.stream():
            chunk_encoded = base64.b64encode(chunk).decode("utf-8")
            request = OsirIpcRequest(action="tus_upload_patch", params={
                "chunk": chunk_encoded,
                "uuid": uuid,
                "tus_resumable": tus_resumable,
                "content_length": len(chunk),
                "content_type": content_type,
                "upload_offset": upload_offset,
                "upload_length": upload_length,
            })
            last_call = OsirIpcResponse.model_validate_json(client.send(request))

            if not "headers" in last_call.response or not "Upload-Offset" in last_call.response["headers"]:
                break

            upload_offset = last_call.response["headers"]['Upload-Offset']

    result = handle_response(last_call)
            
    if isinstance(result, dict) and "headers" in result:
        headers = result.pop("headers")
        return JSONResponse(content=result, headers=headers)
    
    return result
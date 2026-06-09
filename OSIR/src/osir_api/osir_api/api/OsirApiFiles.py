import base64
import os
from typing import Optional

from fastapi import APIRouter, File, Form, Query, UploadFile

from osir_api.api.OsirApiExceptions import UnexpectedExceptionResponse
from osir_api.api.model.OsirApiFilesModel import (
    ArchiveRequest,
    CreateItemRequest,
    DeleteRequest,
    FsData,
    DeleteResult,
    FileOperationResult,
    RenameRequest,
    SaveRequest,
    SearchResult,
    TransferRequest,
    UnarchiveRequest,
)
from fastapi import Response
from osir_api.api.OsirIpcCall import OsirIpcCall
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()


router = APIRouter()


@router.get("/files",
            response_model=FsData,
            responses={400: {}, 404: {}, 500: {"model": UnexpectedExceptionResponse}})
def list_files(path: str = Query(..., description="Directory path (including storage prefix)")):
    return OsirIpcCall("files_list", params={"path": path}, response_only=True)


# @router.post("/files/upload",
#              responses={400: {}, 403: {}, 413: {}, 500: {"model": UnexpectedExceptionResponse}})
# async def upload_files(
#     path: str = Form(..., description="Target directory path (including storage prefix)"),
#     file: UploadFile = File(...),
# ):
#     return OsirIpcCall("files_upload", params={"path": path}, response_only=True)


@router.post("/files/delete",
             response_model=DeleteResult,
             responses={400: {}, 403: {}, 404: {}, 500: {"model": UnexpectedExceptionResponse}})
def delete_files(body: DeleteRequest):
    return OsirIpcCall("files_delete", params={"body": body.model_dump()}, response_only=True)


@router.post("/files/rename",
             response_model=FileOperationResult,
             responses={400: {}, 403: {}, 404: {}, 500: {"model": UnexpectedExceptionResponse}})
def rename_file(body: RenameRequest):
    return OsirIpcCall("files_rename", params={"body": body.model_dump()}, response_only=True)


@router.post("/files/copy",
             response_model=FileOperationResult,
             responses={400: {}, 403: {}, 404: {}, 500: {"model": UnexpectedExceptionResponse}})
def copy_files(body: TransferRequest):
    return OsirIpcCall("files_copy", params={"body": body.model_dump()}, response_only=True)


@router.post("/files/move",
             response_model=FileOperationResult,
             responses={400: {}, 403: {}, 404: {}, 500: {"model": UnexpectedExceptionResponse}})
def move_files(body: TransferRequest):
    return OsirIpcCall("files_move", params={"body": body.model_dump()}, response_only=True)


@router.post("/files/archive",
             response_model=FileOperationResult,
             responses={400: {}, 403: {}, 500: {"model": UnexpectedExceptionResponse}})
def create_archive(body: ArchiveRequest):
    return OsirIpcCall("files_archive", params={"body": body.model_dump()}, response_only=True)


@router.post("/files/unarchive",
             response_model=FileOperationResult,
             responses={400: {}, 403: {}, 404: {}, 500: {"model": UnexpectedExceptionResponse}})
def extract_archive(body: UnarchiveRequest):
    return OsirIpcCall("files_unarchive", params={"body": body.model_dump()}, response_only=True)


@router.post("/files/create-file",
             response_model=FileOperationResult,
             responses={400: {}, 403: {}, 500: {"model": UnexpectedExceptionResponse}})
def create_file(body: CreateItemRequest):
    return OsirIpcCall("files_create_file", params={"body": body.model_dump()}, response_only=True)


@router.post("/files/create-folder",
             response_model=FileOperationResult,
             responses={400: {}, 403: {}, 500: {"model": UnexpectedExceptionResponse}})
def create_folder(body: CreateItemRequest):
    return OsirIpcCall("files_create_folder", params={"body": body.model_dump()}, response_only=True)


@router.get("/files/download",
            responses={400: {}, 404: {}, 500: {"model": UnexpectedExceptionResponse}})
async def download_file(path: str = Query(..., description="Full path to the file (including storage prefix)")):
    # Appel IPC pour récupérer le contenu et le mime_type
    ipc_response = OsirIpcCall("files_download", params={"path": path}, response_only=True)
    # Retourner une réponse FastAPI avec les données binaires
    filename = os.path.basename(ipc_response["filename"])
    content = base64.b64decode(ipc_response["content"])
    return Response(
        content=content,
        media_type=ipc_response["mimeType"],
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/files/search",
            response_model=SearchResult,
            responses={400: {}, 500: {"model": UnexpectedExceptionResponse}})
def search_files(
    path: str = Query(..., description="Base path to search within (including storage prefix)"),
    filter: Optional[str] = Query(None, description="Search query string (e.g. '*.pdf')"),
    deep: bool = Query(False, description="Search subdirectories recursively"),
    size: Optional[str] = Query("all", description="File size filter", enum=["all", "small", "medium", "large"]),
):
    return OsirIpcCall("files_search", params={"path": path, "filter": filter, "deep": deep, "size": size}, response_only=True)


@router.post("/files/save",
             responses={400: {}, 403: {}, 500: {"model": UnexpectedExceptionResponse}})
def save_file(body: SaveRequest):
    return OsirIpcCall("files_save", params={"body": body.model_dump()}, response_only=True)

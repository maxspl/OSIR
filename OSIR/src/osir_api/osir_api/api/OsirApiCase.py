import os
from fastapi import APIRouter
from fastapi import (
    File,
    UploadFile,
    Form,
)
from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse
from osir_api.api.OsirApiExceptions import UnexpectedException, UnexpectedExceptionResponse
from osir_api.api.OsirApiResponse import handle_response
from osir_api.api.model.OsirApiCaseModel import GetCaseListResponse, PostCaseCreateResponse, GetCaseHandlerResponse
from osir_api.api.OsirApiMetadata import API_VERSION
from osir_api.api.model.OsirApiTaskModel import GetTasksListResponse
from osir_api.api.OsirIpcCall import OsirIpcCall
from osir_lib.core.FileManager import FileManager

router = APIRouter()


@router.get("/case",
            response_model=GetCaseListResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def get_case():
    return OsirIpcCall("get_cases")


@router.post("/case/{case_name}",
             response_model=PostCaseCreateResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def create_case(case_name: str):
    return OsirIpcCall("create_case", params={"case_name": case_name})


@router.post("/case/{case_name}/handler",
             response_model=GetCaseHandlerResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def retrieved_case_handler(case_name: str):
    return OsirIpcCall("get_case_handler", params={"case_name": case_name})

@router.post("/case/{case_name}/handler/run",
             response_model=GetCaseHandlerResponse,
             responses={500: {"model": UnexpectedExceptionResponse}})
def start_case_handler(case_name: str):
    return OsirIpcCall("get_case_handler", params={"case_name": case_name})

# Endpoint for file uploads
@router.post("/case/{case_name}/uploads")
async def upload_file(
    case_name: str,
    file: UploadFile = File(...),  # File to be uploaded
    name: str = Form(...),  # Name of the file
    chunk_number: int = Form(0),  # Current chunk number
    total_chunks: int = Form(1),  # Total number of chunks
):
    """
    Handles file uploads with chunked transfer
    (if total_chunks > 1) or single-file upload.
    Files are stored in the case directory.

    Args:
        case_name: Name of the case where files should be uploaded
        file: File to be uploaded
        name: Name of the file
        chunk_number: Current chunk number
        total_chunks: Total number of chunks

    Raises:
        HTTPException: If a validation error occurs
        (e.g., missing data, invalid file size, case not found).
    """
    try:
        case_path = FileManager.get_cases_path(case_name)
        if case_path is None:
            raise UnexpectedException(f"Case '{case_name}' not found")

        chunks_dir = case_path / "chunks"
        uploads_dir = case_path / "uploads"
        chunks_dir.mkdir(exist_ok=True)
        uploads_dir.mkdir(exist_ok=True)

        isLast = (int(chunk_number) + 1) == int(total_chunks)

        file_name = f"{name}_{chunk_number}"

        chunk_path = chunks_dir / file_name
        with open(chunk_path, "wb") as buffer:
            buffer.write(await file.read())

        if isLast: 
            final_file_path = uploads_dir / name
            with open(final_file_path, "wb") as buffer:
                chunk = 0
                while chunk < total_chunks:
                    chunk_file_path = chunks_dir / f"{name}_{chunk}"
                    with open(chunk_file_path, "rb") as infile:
                        buffer.write(infile.read())
                    os.remove(chunk_file_path)
                    chunk += 1

            response = OsirIpcResponse(
                version=API_VERSION,
                status=200,
                message="File Uploaded",
                response={"file_path": str(final_file_path), "file_name": name}
            )
            return handle_response(response)

        response = OsirIpcResponse(
            version=API_VERSION,
            status=200,
            message="Chunk Uploaded",
            response={"chunk_number": chunk_number, "total_chunks": total_chunks}
        )
        return handle_response(response)

    except Exception as e:
        raise UnexpectedException(str(e))


@router.get("/case/{case_name}/tasks",
            response_model=GetTasksListResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def get_tasks(case_name: str):
    return OsirIpcCall("get_tasks", params={"case_name": case_name})


"""
IPC handlers for uploads operations in OSIR.
"""

import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from uuid import UUID, uuid4

from osir_service.ipc.model.OsirFileModel import DirEntry, FsData
from osir_service.ipc.model.OsirIpcRequest import OsirIpcRequest
from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse
from osir_service.ipc.model.OsirExceptions import OsirException
from osir_lib.core.OsirConstants import OSIR, OSIR_PATHS

from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

from pydantic import BaseModel, Field

class OsirTusFile(BaseModel):
    uuid: str
    offset: int = 0 
    size: int | None 
    is_size_deferred: bool = False 
    metadata: dict[str, str] = {} 
    is_partial: bool = False
    is_final: bool = True 
    partial_uploads: List[str] = [] 
    expires: str | None
    storage_path: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    entry: DirEntry = None

FILESTORE: dict[UUID, OsirTusFile] = {}

class TusConfig:
    tus_version: str = "1.0.0"
    tus_resumable: str = "1.0.0"
    tus_checksum_algorithm: str = "md5,sha1,crc32"
    tus_max_size: int = 10 * 1024 * 1024 * 1024  # 10GB
    tus_extension: str = "creation,creation-defer-length,creation-with-upload,expiration,termination"
    location: str = "proxy/api/files/upload"

class OsirIpcTus:

    @staticmethod
    def handle_tus_upload_options(req: OsirIpcRequest, resp: OsirIpcResponse):
        return OsirIpcResponse(
            response={
                "headers": {
                    "Tus-Resumable": TusConfig.tus_resumable,
                    "Tus-Checksum-Algorithm": TusConfig.tus_checksum_algorithm,
                    "Tus-Version": TusConfig.tus_version,
                    "Tus-Max-Size": str(TusConfig.tus_max_size),
                    "Tus-Extension": TusConfig.tus_extension,
                }
            }
        )

    @staticmethod
    def handle_tus_upload_head(req: OsirIpcRequest, resp: OsirIpcResponse):
        uuid = req.params.get("uuid")
        info = FILESTORE.get(uuid)

        if info is None:
            return OsirIpcResponse(
                status=404,
                response={"error": "File not found"}
            )

        headers = {
            "Tus-Resumable": TusConfig.tus_version,
            "Upload-Length": str(info.size),
            "Upload-Offset": str(info.offset),
            "Cache-Control": "no-store",
        }

        if info.is_size_deferred:
            headers["Upload-Defer-Length"] = str(1)

        if info.metadata:
            metadata_base64 = ",".join(
                f"{key} {base64.b64encode(bytes(value, 'utf-8')).decode('utf-8')}"
                for key, value in info.metadata.items()
            )
            headers["Upload-Metadata"] = metadata_base64

        return OsirIpcResponse(
            response={"headers": headers}
        )

    @staticmethod
    def handle_tus_upload_post(req: OsirIpcRequest, resp: OsirIpcResponse):
        upload_metadata = req.params.get("upload_metadata")
        upload_length = int(req.params.get("upload_length"))
        upload_defer_length = req.params.get("upload_defer_length")
        content_length = int(req.params.get("content_length"))
        content_type = req.params.get("content_type")

        if upload_defer_length is not None and upload_defer_length != 1:
            return OsirIpcResponse(
                status=400,
                response={"error": "Upload-Defer-Length Must be not set or set as 1!"}
            )

        if upload_length is None and upload_defer_length is None:
            return OsirIpcResponse(
                status=400,
                response={"error": "Upload-Defer-Length Must set as 1 because no Upload-Length specified!"}
            )

        is_size_deferred = upload_length is None or upload_length <= 0

        metadata = {}
        if upload_metadata and upload_metadata != "":
            for kv in upload_metadata.split(","):
                key, value = kv.rsplit(" ", 1)
                decoded_value = base64.b64decode(value.strip()).decode("utf-8")
                metadata[key.strip()] = decoded_value

        if not "path" in metadata or not "name" in metadata:
            return OsirIpcResponse(
                status=400,
                response={"error": "Path not specified, are you using vue-finder ?"}
            )

        storage_path: str = metadata["path"]
        if not storage_path.endswith("//"):
            storage_path += '/'

        case_name, path = FsData.get_real_path(storage_path + metadata['name'])
        case_candidate = Path(OSIR_PATHS.CASES_DIR / case_name).resolve()
        path_canditate = case_candidate / path

        if not FsData.is_secure(path_canditate, case_candidate):
            return OsirIpcResponse(
                status=400,
                response={"error": "Path is not secure, must be in OSIR/share/cases !"}
            )

        upload_uuid = str(uuid4().hex)
        file = OsirTusFile(
            uuid=upload_uuid,
            offset=0,
            size=upload_length,
            is_size_deferred=is_size_deferred,
            storage_path=str(path_canditate),
            metadata=metadata,
            expires=None,
            entry=DirEntry.from_path(path_canditate, case_name)
        )

        if not file.entry.create_bin():
            return OsirIpcResponse(
                status=400,
                response={"error": "A file with this name already exists !"}
            )
        
        if content_length and upload_length and not is_size_deferred:
            if content_type != "application/offset+octet-stream":
                return OsirIpcResponse(
                    status=400,
                    response={"error": "Content-Type Must be application/offset+octet-stream!"}
                )

            file = OsirIpcTus._write_chunk(req, file)
            
            if not file:
                return OsirIpcResponse(
                    status=412,
                    response={
                        "headers": {
                            "Tus-Resumable": TusConfig.tus_resumable,
                        }
                    }
                )

            
            date_expiry = datetime.now() + timedelta(days=1)
            file.expires = str(date_expiry.isoformat())
            FILESTORE[upload_uuid] = file
            
            return OsirIpcResponse(
                status=204,
                response={
                    "headers": {
                        "Location": f"{TusConfig.location}/{upload_uuid}",
                        "Tus-Resumable": TusConfig.tus_resumable,
                        "Upload-Offset": str(file.offset),
                        "Upload-Expires": str(file.expires),
                    }
                }
            )

        else:
            FILESTORE[upload_uuid] = file
            return OsirIpcResponse(
                status=201,
                response={
                    "headers": {
                        "Location": f"{TusConfig.location}/{upload_uuid}",
                        "Tus-Resumable": TusConfig.tus_resumable,
                    }
                }
            )

    @staticmethod
    def handle_tus_upload_patch(req: OsirIpcRequest, resp: OsirIpcResponse):
        uuid = req.params.get("uuid")
        tus_resumable = req.params.get("tus_resumable")
        content_length = req.params.get("content_length")
        content_type = req.params.get("content_type")
        upload_offset = req.params.get("upload_offset")
        upload_length = req.params.get("upload_length")

        if tus_resumable != TusConfig.tus_version:
            return OsirIpcResponse(
                status=400,
                response={"error": "Invalid Tus-Resumable!"}
            )

        if content_type != "application/offset+octet-stream":
            return OsirIpcResponse(
                status=400,
                response={"error": "Invalid Content-Type!"}
            )

        if uuid not in FILESTORE:
            return OsirIpcResponse(
                status=404,
                response={
                    "headers": {
                        "Tus-Resumable": TusConfig.tus_resumable,
                    }
                }
            )
        
        file = FILESTORE[uuid]

        if file.is_size_deferred:
            if upload_length is None:
                return OsirIpcResponse(
                    status=412,
                    response={
                        "headers": {
                            "Tus-Resumable": TusConfig.tus_resumable,
                        }
                    }
                )

            if not file.size and upload_length:
                file.size = upload_length

        lock = file.entry.new_lock()
        with lock:
            if int(upload_offset) != file.offset:
                logger.info(f"{upload_offset} upload, file offset {file.offset}")
                return OsirIpcResponse(
                    status=409,
                    response={
                        "headers": {
                            "Tus-Resumable": TusConfig.tus_resumable,
                        }
                    }
                )

            file = OsirIpcTus._write_chunk(req, file)

        if int(upload_offset) + int(content_length) != file.offset:
            return OsirIpcResponse(
                status=460,
                response={
                    "headers": {
                        "Tus-Resumable": TusConfig.tus_resumable,
                    }
                }
            )

        date_expiry = datetime.now() + timedelta(days=1)
        file.expires = str(date_expiry.isoformat())

        headers = {
            "Location": f"{TusConfig.location}/{uuid}",
            "Tus-Resumable": TusConfig.tus_resumable,
            "Upload-Offset": str(file.offset),
            "Upload-Expires": str(file.expires),
        }

        return OsirIpcResponse(
            status=204,
            response={"headers": headers}
        )

    @staticmethod
    def _write_chunk(req: OsirIpcRequest, info: OsirTusFile) -> OsirTusFile:
        f = info.entry.open()

        try:
            chunk_encoded = req.params.get("chunk")
            chunk = base64.b64decode(chunk_encoded)
            chunk_size = len(chunk)
            f.write(chunk)
            info.offset += chunk_size
        finally:
            f.close()

        return info
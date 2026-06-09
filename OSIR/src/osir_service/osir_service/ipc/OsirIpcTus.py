"""
IPC handlers for uploads operations in OSIR.
"""

import base64
from datetime import datetime, timedelta
from uuid import uuid4

from osir_service.ipc.model.OsirFileModel import FileInfo, FsData
from osir_service.ipc.model.OsirIpcRequest import OsirIpcRequest
from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse
from osir_service.ipc.model.OsirExceptions import OsirException
from osir_lib.core.OsirConstants import OSIR

from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

from pydantic import BaseModel

class TusConfig:
    tus_version: str = "1.0.0"
    tus_resumable: str = "1.0.0"
    tus_checksum_algorithm: str = "md5,sha1,crc32"
    tus_max_size: int = 10 * 1024 * 1024 * 1024  # 10GB
    tus_extension: str = "creation,creation-defer-length,creation-with-upload,expiration,termination"
    location: str = "proxy/api/files/upload"  # Chemin de base pour les uploads

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
    def handle_tus_upload_post(req: OsirIpcRequest, resp: OsirIpcResponse):
        # Récupération des paramètres depuis req.params
        upload_metadata = req.params.get("upload_metadata")
        upload_length = req.params.get("upload_length")
        upload_defer_length = req.params.get("upload_defer_length")
        content_length = req.params.get("content_length")
        content_type = req.params.get("content_type")

        # Validation des paramètres
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

        # Parsing des métadonnées
        metadata = {}
        if upload_metadata and upload_metadata != "":
            for kv in upload_metadata.split(","):
                key, value = kv.rsplit(" ", 1)
                decoded_value = base64.b64decode(value.strip()).decode("utf-8")
                metadata[key.strip()] = decoded_value

        # Génération d'un UUID pour le fichier
        uuid = str(uuid4().hex)

        # Création de l'objet FileInfo
        info = FileInfo(
            uuid=uuid,
            offset=0,
            size=upload_length,
            is_size_deferred=is_size_deferred,
            storage={},
            metadata=metadata,
            expires=None,
        )

        # Écriture des infos dans le datastore
        # req.instance.datastore.write_file_info(info)
        # req.instance.datastore.new_file_bin(uuid=uuid)
        logger.info(info)
        logger.info(req.params)

        if content_length and upload_length and not is_size_deferred:
            if content_type != "application/offset+octet-stream":
                return OsirIpcResponse(
                    status=400,
                    response={"error": "Content-Type Must be application/offset+octet-stream!"}
                )

            info = OsirIpcTus._write_chunk(req, info)
            if not info:
                return OsirIpcResponse(
                    status=412,
                    response={
                        "headers": {
                            "Tus-Resumable": TusConfig.tus_resumable,
                        }
                    }
                )

            date_expiry = datetime.now() + timedelta(days=1)
            info.expires = str(date_expiry.isoformat())
            # req.instance.datastore.write_file_info(info)

            return OsirIpcResponse(
                status=204,
                response={
                    "headers": {
                        "Location": f"{TusConfig.location}/{uuid}",
                        "Tus-Resumable": TusConfig.tus_resumable,
                        "Upload-Offset": str(info.offset),
                        "Upload-Expires": str(info.expires),
                    }
                }
            )

        # Cas 2 : Création sans upload (Upload-Length non fourni ou égal à 0)
        else:
            return OsirIpcResponse(
                status=201,
                response={
                    "headers": {
                        "Location": f"{TusConfig.location}/{uuid}",
                        "Tus-Resumable": TusConfig.tus_resumable,
                    }
                }
            )

    @staticmethod
    def handle_tus_upload_patch(req: OsirIpcRequest, resp: OsirIpcResponse):
        # Récupération des paramètres
        uuid = req.params.get("uuid")
        tus_resumable = req.params.get("tus_resumable")
        content_length = req.params.get("content_length")
        content_type = req.params.get("content_type")
        upload_offset = req.params.get("upload_offset")
        upload_length = req.params.get("upload_length")

        # logger.info(info)
        logger.info(req.params)

        # Validation des headers
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

        # Vérification de l'existence du fichier
        info = req.instance.datastore.read_file_info(uuid)
        if info is None:
            return OsirIpcResponse(
                status=404,
                response={
                    "headers": {
                        "Tus-Resumable": TusConfig.tus_resumable,
                    }
                }
            )

        # Gestion de la taille différée
        if info.is_size_deferred:
            if upload_length is None:
                return OsirIpcResponse(
                    status=412,
                    response={
                        "headers": {
                            "Tus-Resumable": TusConfig.tus_resumable,
                        }
                    }
                )

            if not info.size and upload_length:
                info.size = upload_length
                req.instance.datastore.write_file_info(info)

        # Vérification du verrou et de l'offset
        lock = req.instance.datastore.new_lock(uuid)
        with lock:
            if upload_offset != info.offset:
                return OsirIpcResponse(
                    status=409,
                    response={
                        "headers": {
                            "Tus-Resumable": TusConfig.tus_resumable,
                        }
                    }
                )

            # Simulation de l'écriture du chunk
            info = OsirIpcTus._write_chunk(req, info)

        # Vérification de la taille réelle du fichier
        if upload_offset + content_length != info.offset:
            return OsirIpcResponse(
                status=460,
                response={
                    "headers": {
                        "Tus-Resumable": TusConfig.tus_resumable,
                    }
                }
            )

        # Mise à jour de l'expiration
        date_expiry = datetime.now() + timedelta(days=1)
        info.expires = str(date_expiry.isoformat())
        req.instance.datastore.write_file_info(info)

        # Réponse finale
        headers = {
            "Location": f"{TusConfig.location}/{uuid}",
            "Tus-Resumable": TusConfig.tus_resumable,
            "Upload-Offset": str(info.offset),
            "Upload-Expires": str(info.expires),
        }

        return OsirIpcResponse(
            status=204,
            response={"headers": headers}
        )

    # @staticmethod
    # async def _write_chunk(request: Request, info: FileInfo) -> FileInfo:
    #     f = self.datastore.open(info.uuid)

    #     try:
    #         async for chunk in request.stream():
    #             chunk_size = len(chunk)
    #             f.write(chunk)
    #             info.offset += chunk_size
    #             # info.chunk_size = chunk_size
    #             # info.part += 1
    #     except ClientDisconnect as e:
    #         print(f"Client disconnected: {e}")
    #     finally:
    #         self.datastore.write_file_info(info)
    #         f.close()

    #     return info
"""
IPC handlers for file operations in OSIR.
"""

import base64

from osir_service.ipc.model.OsirFileModel import FsData
from osir_service.ipc.model.OsirIpcRequest import OsirIpcRequest
from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse
from osir_service.ipc.model.OsirExceptions import OsirException
from osir_lib.core.OsirConstants import OSIR

from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

class OsirIpcFiles:
    """
    File operation handlers for IPC.
    These functions are called by the handlers registered in OsirIpc.py
    """
    
    @staticmethod
    def handle_files_list(req: OsirIpcRequest, resp: OsirIpcResponse = None) -> OsirIpcResponse:
        """Handler for listing files and directories."""
        try:
            path = req.params.get("path")
            if not path:
                return OsirException.MISSING_PARAMETER("path")
            return OsirIpcResponse(response=FsData.from_path(path).model_dump())
        except ValueError as e:
            return OsirException.VALIDATION_ERROR(str(e), {"parameter": "path"})
        except Exception as e:
            return OsirException.FILE_OPERATION_ERROR(str(e), "list")
    
    @staticmethod
    def handle_files_upload(req: OsirIpcRequest, resp: OsirIpcResponse = None) -> OsirIpcResponse:
        """Handler for file upload."""
        return OsirIpcResponse(
            status=501,
            message="Not implemented",
            response={"error": "Not implemented"}
        )
    
    @staticmethod
    def handle_files_delete(req: OsirIpcRequest, resp: OsirIpcResponse = None) -> OsirIpcResponse:
        """Handler for deleting files/directories."""
        body = req.params.get('body', {})
        try:
            path = body.get("path")
            items = body.get("items", [])
            
            if not path:
                return OsirException.MISSING_PARAMETER("path")
            if not items:
                return OsirException.MISSING_PARAMETER("items")
            
            deleted = []
            for item in items:
                item_path = item.get("path")
                if not item_path:
                    return OsirException.MISSING_PARAMETER("item.path")
                deleted_fsdata = FsData.delete_item(item_path)
                if deleted_fsdata:
                    deleted.append({**deleted_fsdata.model_dump()})
            
            return OsirIpcResponse(
                response={"deleted": deleted, **FsData.from_path(path).model_dump()}
            )
        except ValueError as e:
            return OsirException.VALIDATION_ERROR(str(e))
        except Exception as e:
            return OsirException.FILE_OPERATION_ERROR(str(e), "delete")
    
    @staticmethod
    def handle_files_rename(req: OsirIpcRequest, resp: OsirIpcResponse = None) -> OsirIpcResponse:
        """Handler for renaming a file/directory."""
        body = req.params.get('body', {})
        try:
            path = body.get('path', '')
            item = body.get('item', '')
            new_name = body.get('name', '')
            
            if not path:
                return OsirException.MISSING_PARAMETER("path")
            if not item:
                return OsirException.MISSING_PARAMETER("item")
            if not new_name:
                return OsirException.MISSING_PARAMETER("name")
            
            renamed = FsData.rename_item(item, new_name)
            return OsirIpcResponse(
                response={**FsData.from_path(path).model_dump()}
            )
        except ValueError as e:
            return OsirException.VALIDATION_ERROR(str(e))
        except Exception as e:
            return OsirException.FILE_OPERATION_ERROR(str(e), "rename")
    
    @staticmethod
    def handle_files_copy(req: OsirIpcRequest, resp: OsirIpcResponse = None) -> OsirIpcResponse:
        """Handler for copying files/directories."""
        body = req.params.get('body', {})
        try:
            sources = body.get('sources', [])
            destination = body.get('destination', '')
            path = body.get('path', '')

            if not sources:
                return OsirException.MISSING_PARAMETER("sources")
            if not destination:
                return OsirException.MISSING_PARAMETER("destination")
            if not path:
                return OsirException.MISSING_PARAMETER("path")
            
            FsData.copy_items(sources, destination)
            return OsirIpcResponse(
                response={**FsData.from_path(path).model_dump()}
            )
        except ValueError as e:
            return OsirException.VALIDATION_ERROR(str(e))
        except Exception as e:
            return OsirException.FILE_OPERATION_ERROR(str(e), "copy")
    
    @staticmethod
    def handle_files_move(req: OsirIpcRequest, resp: OsirIpcResponse = None) -> OsirIpcResponse:
        """Handler for moving files/directories."""
        body = req.params.get('body', {})
        try:
            sources = body.get('sources', [])
            destination = body.get('destination', '')
            path = body.get('path', '')

            if not sources:
                return OsirException.MISSING_PARAMETER("sources")
            if not destination:
                return OsirException.MISSING_PARAMETER("destination")
            if not path:
                return OsirException.MISSING_PARAMETER("path")
            
            FsData.move_items(sources, destination)
            return OsirIpcResponse(
                response={**FsData.from_path(path).model_dump()}
            )
        except ValueError as e:
            return OsirException.VALIDATION_ERROR(str(e))
        except Exception as e:
            return OsirException.FILE_OPERATION_ERROR(str(e), "move")
    
    @staticmethod
    def handle_files_archive(req: OsirIpcRequest, resp: OsirIpcResponse = None) -> OsirIpcResponse:
        """Handler for creating archives."""
        body = req.params.get('body', {})
        try:
            items = body.get('items', [])
            archive_path = body.get('path', '')
            archive_name = body.get('name', 'archive')
            
            if not items:
                return OsirException.MISSING_PARAMETER("items")
            if not archive_path:
                return OsirException.MISSING_PARAMETER("path")
            
            FsData.archive_items(items, archive_path, archive_name)
            return OsirIpcResponse(
                response={**FsData.from_path(archive_path).model_dump()}
            )
        except ValueError as e:
            return OsirException.VALIDATION_ERROR(str(e))
        except Exception as e:
            return OsirException.FILE_OPERATION_ERROR(str(e), "archive")
    
    @staticmethod
    def handle_files_unarchive(req: OsirIpcRequest, resp: OsirIpcResponse = None) -> OsirIpcResponse:
        """Handler for extracting archives."""
        body = req.params.get('body', {})
        try:
            item_path = body.get('item', '')
            target_path = body.get('path', '')
            
            if not item_path:
                return OsirException.MISSING_PARAMETER("item")
            if not target_path:
                return OsirException.MISSING_PARAMETER("path")
            
            FsData.unarchive_item(item_path, target_path)
            return OsirIpcResponse(
                response={**FsData.from_path(target_path).model_dump()}
            )
        except ValueError as e:
            return OsirException.VALIDATION_ERROR(str(e))
        except Exception as e:
            return OsirException.FILE_OPERATION_ERROR(str(e), "unarchive")
    
    @staticmethod
    def handle_files_create_folder(req: OsirIpcRequest, resp: OsirIpcResponse = None) -> OsirIpcResponse:
        """Handler for creating a directory."""
        body = req.params.get('body', {})
        try:
            path = body.get('path', '')
            name = body.get('name', '')
            
            if not path:
                return OsirException.MISSING_PARAMETER("path")
            if not name:
                return OsirException.MISSING_PARAMETER("name")
            
            FsData.create_folder(path, name)
            return OsirIpcResponse(
                response={**FsData.from_path(path).model_dump()}
            )
        except ValueError as e:
            return OsirException.VALIDATION_ERROR(str(e))
        except Exception as e:
            return OsirException.FILE_OPERATION_ERROR(str(e), "create_folder")
    
    @staticmethod
    def handle_files_download(req: OsirIpcRequest, resp: OsirIpcResponse = None) -> OsirIpcResponse:
        """Handler for downloading a file."""
        try:
            path = req.params.get('path', '')
            
            if not path:
                return OsirException.MISSING_PARAMETER("path")
            
            content, mime_type, filename = FsData.download_file(path)
            return OsirIpcResponse(
                response={
                    "content": base64.b64encode(content).decode('utf-8'),
                    "mimeType": mime_type,
                    "filename": filename
                }
            )
        except ValueError as e:
            return OsirException.VALIDATION_ERROR(str(e))
        except FileNotFoundError as e:
            return OsirException.FILE_NOT_FOUND(str(e))
        except Exception as e:
            return OsirException.IO_ERROR(str(e))
    
    @staticmethod
    def handle_files_search(req: OsirIpcRequest, resp: OsirIpcResponse = None) -> OsirIpcResponse:
        """Handler for searching files."""
        try:
            path = req.params.get('path', '')
            filter_expr = req.params.get('filter', None)
            deep = req.params.get('deep', False)
            size_filter = req.params.get('size', 'all')
            
            files = FsData.search_files(path, filter_expr, deep, size_filter)
            return OsirIpcResponse(
                response={
                    "dirname": path,
                    "files": [f.model_dump() for f in files],
                    "storages": FsData.from_path(path).storages
                }
            )
        except ValueError as e:
            return OsirException.VALIDATION_ERROR(str(e))
        except Exception as e:
            return OsirException.FILE_OPERATION_ERROR(str(e), "search")
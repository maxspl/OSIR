
from typing import List, Literal, Optional
from pydantic import BaseModel

"""
==========================================
Schema: DirEntry
==========================================
Description: Represents a file or directory entry.
==========================================
"""


class DirEntry(BaseModel):
    dir: str
    basename: str
    extension: str
    path: str
    storage: str
    type: Literal["file", "dir"]
    visibility: str
    file_size: Optional[int] = None
    last_modified: Optional[int] = None
    mime_type: Optional[str] = None
    read_only: Optional[bool] = None
    previewUrl: Optional[str] = None


"""
==========================================
Schema: FsData
==========================================
Description: Response for GET / (list files).
==========================================
"""


class FsData(BaseModel):
    storages: List[str]
    dirname: str
    files: List[DirEntry]
    read_only: bool


"""
==========================================
Schema: FileOperationResult
==========================================
Description: Base response for file mutation operations.
==========================================
"""


class FileOperationResult(BaseModel):
    files: List[DirEntry]
    storages: List[str]
    read_only: bool
    dirname: str


"""
==========================================
Schema: DeleteResult
==========================================
Description: Response for POST /delete — extends FileOperationResult.
==========================================
"""


class DeleteResult(FileOperationResult):
    deleted: Optional[List[DirEntry]] = None


"""
==========================================
Schema: FileContentResult
==========================================
Description: Response for file content retrieval.
==========================================
"""


class FileContentResult(BaseModel):
    content: str
    mimeType: Optional[str] = None


"""
==========================================
Schema: SearchResult
==========================================
Description: Response for GET /search.
==========================================
"""


class SearchResult(BaseModel):
    dirname: str
    files: List[DirEntry]
    storages: List[str]


"""
==========================================
Schema: ErrorResponse
==========================================
Description: Generic error response.
==========================================
"""


class ErrorResponse(BaseModel):
    message: str
    code: Optional[str] = None
    status: Optional[bool] = None


"""
==========================================
Request bodies
==========================================
"""


class DeleteItem(BaseModel):
    path: str
    type: Literal["file", "dir"]


class DeleteRequest(BaseModel):
    path: str
    items: List[DeleteItem]


class RenameRequest(BaseModel):
    path: str
    item: str
    name: str


class TransferRequest(BaseModel):
    sources: List[str]
    destination: str
    path: str


class ArchiveItem(BaseModel):
    path: str
    type: Literal["file", "dir"]


class ArchiveRequest(BaseModel):
    items: List[ArchiveItem]
    path: str
    name: str


class UnarchiveRequest(BaseModel):
    item: str
    path: str


class CreateItemRequest(BaseModel):
    path: str
    name: str


class SaveRequest(BaseModel):
    path: str
    content: str

from typing import List, Literal, Optional, Tuple, Dict
from pydantic import BaseModel
from osir_service.ipc.OsirIpc import FileManager
from osir_lib.core.OsirConstants import OSIR_PATHS, Path
import mimetypes
import os
import tarfile
import zipfile
import shutil
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()


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

    @staticmethod
    def get_virt_path(case_name: str, path: Path):
        candidate = Path(OSIR_PATHS.CASES_DIR / case_name).resolve()

        if candidate.exists():
            relative_path = path.relative_to(candidate)
            return f"{case_name}://{str(relative_path)}"

    @classmethod
    def from_path(cls, path: Path, case_name: str) -> "DirEntry":
        mimetypes.init()
        virt_path = DirEntry.get_virt_path(case_name, path)
        parent_virt_path = ""

        if not path.parent.samefile(OSIR_PATHS.CASES_DIR):
            parent_virt_path = DirEntry.get_virt_path(case_name, path.parent)

        if not virt_path:
            if path.is_file():
                virt_path = f"{case_name}://{path.name}"
            else:
                virt_path = f"{path.name}://"
                case_name = path.name
    
        return cls(
            dir=parent_virt_path,
            basename=path.name,
            extension=path.suffix,
            path=virt_path,
            storage=case_name,
            type="file" if path.is_file() else "dir",
            visibility="public",
            file_size=path.stat().st_size if path.is_file() else None,
            last_modified=int(path.stat().st_mtime) if path.exists() else None,
            mime_type=mimetypes.guess_type(str(path))[0] if path.is_file() else None,
            read_only=not os.access(path, os.W_OK) if path.exists() else False,
            previewUrl=None
        )


class FsData(BaseModel):
    storages: List[str]
    dirname: str
    files: List[DirEntry]
    read_only: bool 

    @classmethod
    def from_path(cls, path: str) -> "FsData":
        # path format : CASE_NAME//PATH
        selected_storage, virt_path = FsData.get_real_path(storage_path=path)
        storages = FileManager.all_cases()

        return cls(
            storages=storages,
            dirname=path,
            files=FsData.get_files(selected_storage, virt_path),
            read_only=False
        )

    @staticmethod
    def get_real_path(storage_path: str) -> tuple[str, str]:
        if '://' not in storage_path:
            raise ValueError("Path must contain '://'")
        case_name, path = storage_path.split('://', 1)
        return case_name, path
    
    @staticmethod
    def get_path(case_name: str, virt_path: str) -> Path:
        candidate = Path(OSIR_PATHS.CASES_DIR / case_name / virt_path).resolve()
        return candidate if candidate.exists() else OSIR_PATHS.CASES_DIR

    @staticmethod
    def get_absolute_path(storage_path: str):
        if '://' not in storage_path:
            raise ValueError("Path must contain '://'")
        case_name, path = storage_path.split('://', 1)
        abs_path = FsData.get_path(case_name, path)

        if not FsData.is_secure(abs_path, case_name):
            return None
        
        return abs_path
        
    @staticmethod
    def get_files(case_name: str, virt_path: Path):
        path = FsData.get_path(case_name, virt_path)
        return [DirEntry.from_path(item, case_name).model_dump() for item in sorted(path.iterdir())]
    
    @staticmethod
    def delete_item(storage_path: Path) -> DirEntry:
        case_name, virt_path = FsData.get_real_path(storage_path=storage_path)
        path = FsData.get_path(case_name, virt_path)

        if not FsData.is_secure(path, case_name):
            logger.warning(f"Path to delete is not secured: {path}")
            raise ValueError(f"Path is not secured: {storage_path}")
        
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {storage_path}")
        
        deleted = DirEntry.from_path(path, case_name)

        if path.is_file():
            path.unlink()
            return deleted
        elif path.is_dir():
            shutil.rmtree(path)
            return deleted

        raise ValueError(f"Cannot delete: {storage_path}")
    
    @staticmethod
    def is_secure(path: Path, case_name: str) -> bool:
        base_dir = Path(OSIR_PATHS.CASES_DIR).resolve()
        candidate = (base_dir / case_name).resolve()

        try:
            resolved_path = path.resolve()
        except (OSError, RuntimeError):
            return False

        return resolved_path.is_relative_to(base_dir) and resolved_path.is_relative_to(candidate)

    @staticmethod
    def rename_item(item: str, new_name: str) -> DirEntry:
        """Rename an item in a directory."""
        case_name, virt_path = FsData.get_real_path(item)
        dir_path = FsData.get_path(case_name, virt_path)
        
        if not FsData.is_secure(dir_path, case_name):
            raise ValueError(f"Path is not secured: {dir_path} / {case_name}")

        if not dir_path.exists():
            raise FileNotFoundError(f"Path not found: {dir_path}")

        new_path = dir_path.parent / new_name

        if new_path.exists():
            raise ValueError("Destination path already exists")
        
        if not FsData.is_secure(new_path, case_name):
            raise ValueError("Destination path is not secured")

        dir_path.rename(new_path)

        return DirEntry.from_path(new_path, case_name)

    @staticmethod
    def copy_items(sources: List[str], destination: str) -> List[DirEntry]:
        """Copy items to a destination directory."""
        copied = []
        dest_case_name, dest_virt_path = FsData.get_real_path(destination)
        dest_path = FsData.get_path(dest_case_name, dest_virt_path)
        
        if not FsData.is_secure(dest_path, dest_case_name):
            logger.warning(f"Destination path is not secured: {dest_path}")
            raise ValueError("Destination path is not secured")
        
        if not dest_path.exists() or not dest_path.is_dir():
            raise ValueError(f"Destination not found or not a directory: {destination}")
        
        for source in sources:
            src_case_name, src_virt_path = FsData.get_real_path(source)
            src_path = FsData.get_path(src_case_name, src_virt_path)
            
            if not FsData.is_secure(src_path, src_case_name):
                logger.warning(f"Source path is not secured: {src_path}")
                raise ValueError(f"Source path is not secured: {source}")
            
            if not src_path.exists():
                raise ValueError(f"Source not found: {source}")
            
            dest_item = dest_path / src_path.name
            
            if dest_item.exists():
                raise ValueError("Destination path already exists")
        
            if src_path.is_dir():
                shutil.copytree(src_path, dest_item)
            else:
                shutil.copy2(src_path, dest_item)
            
            copied.append(DirEntry.from_path(dest_item, dest_case_name))
        
        return copied

    @staticmethod
    def move_items(sources: List[str], destination: str) -> List[DirEntry]:
        """Move items to a destination directory."""
        moved = []
        dest_case_name, dest_virt_path = FsData.get_real_path(destination)
        dest_path = FsData.get_path(dest_case_name, dest_virt_path)
        
        if not FsData.is_secure(dest_path, dest_case_name):
            logger.warning(f"Destination path is not secured: {dest_path}")
            raise ValueError("Destination path is not secured")
        
        if not dest_path.exists() or not dest_path.is_dir():
            raise ValueError(f"Destination not found or not a directory: {destination}")
        
        for source in sources:
            src_case_name, src_virt_path = FsData.get_real_path(source)
            src_path = FsData.get_path(src_case_name, src_virt_path)
            
            if not FsData.is_secure(src_path, src_case_name):
                logger.warning(f"Source path is not secured: {src_path}")
                raise ValueError(f"Source path is not secured: {source}")
            
            if not src_path.exists():
                raise ValueError(f"Source not found: {source}")
            
            dest_item = dest_path / src_path.name

            if dest_item.exists():
                raise ValueError("Destination path already exists")
            
            shutil.move(str(src_path), str(dest_item))
            moved.append(DirEntry.from_path(dest_item, dest_case_name))
        
        return moved

    @staticmethod
    def archive_items(items: List[Dict[str, str]], archive_path: str, archive_name: str) -> Optional[DirEntry]:
        """Create an archive (tar.gz) containing the specified items."""
        archive_case_name, archive_virt_path = FsData.get_real_path(archive_path)
        archive_dir = FsData.get_path(archive_case_name, archive_virt_path)
        
        if not FsData.is_secure(archive_dir, archive_case_name):
            logger.warning(f"Archive directory is not secured: {archive_dir}")
            raise ValueError("Archive directory is not secured")
        
        if not archive_dir.exists() or not archive_dir.is_dir():
            raise ValueError(f"Archive directory not found: {archive_path}")
        
        archive_real_path = archive_dir / archive_name
        
        if archive_real_path.exists():
            raise ValueError("Destination path already exists")
        
        with zipfile.ZipFile(archive_real_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for item in items:
                item_path = item.get('path', '')
                item_case_name, item_virt_path = FsData.get_real_path(item_path)
                item_real = FsData.get_path(item_case_name, item_virt_path)

                if not FsData.is_secure(item_real, item_case_name):
                    logger.warning(f"Item path is not secured: {item_real}")
                    raise ValueError(f"Item path is not secured: {item_path}")

                if not item_real.exists():
                    raise ValueError(f"Item not found: {item_path}")

                # Si c'est un fichier, on l'ajoute directement
                if item_real.is_file():
                    arcname = os.path.relpath(item_real, archive_dir)
                    zipf.write(str(item_real), arcname=arcname)
                # Si c'est un dossier, on parcourt récursivement
                elif item_real.is_dir():
                    for root, _, files in os.walk(item_real):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, archive_dir)
                            zipf.write(str(file_path), arcname=arcname)
        
        return DirEntry.from_path(archive_real_path, archive_case_name)

    @staticmethod
    def unarchive_item(item_path: str, target_path: str) -> List[DirEntry]:
        """Extract an archive to a target directory."""
        item_case_name, item_virt_path = FsData.get_real_path(item_path)
        item_real = FsData.get_path(item_case_name, item_virt_path)
        
        target_case_name, target_virt_path = FsData.get_real_path(target_path)
        target_real = FsData.get_path(target_case_name, target_virt_path)
        
        if not FsData.is_secure(item_real, item_case_name):
            logger.warning(f"Archive path is not secured: {item_real}")
            raise ValueError("Archive path is not secured")
        
        if not FsData.is_secure(target_real, target_case_name):
            logger.warning(f"Target path is not secured: {target_real}")
            raise ValueError("Target path is not secured")
        
        if not item_real.exists():
            raise ValueError(f"Archive not found: {item_path}")
        
        if not target_real.exists() or not target_real.is_dir():
            raise ValueError(f"Target directory not found: {target_path}")
        
        if item_real.suffix in ['.tar.gz', '.tgz']:
            with tarfile.open(item_real, "r:gz") as tar:
                tar.extractall(path=str(target_real))
        elif item_real.suffix == '.tar':
            with tarfile.open(item_real, "r:") as tar:
                tar.extractall(path=str(target_real))
        elif item_real.suffix == '.zip':
            with zipfile.ZipFile(item_real, 'r') as zip_ref:
                zip_ref.extractall(str(target_real))
        else:
            raise ValueError(f"Unsupported archive format: {item_real.suffix}")
        
        extracted = []
        for item in target_real.iterdir():
            if item.is_file():
                extracted.append(DirEntry.from_path(item, target_case_name))
            elif item.is_dir():
                extracted.append(DirEntry.from_path(item, target_case_name))
        
        return extracted

    @staticmethod
    def create_folder(storage_path: str, name: str) -> Optional[DirEntry]:
        """Create a new directory."""
        case_name, virt_path = FsData.get_real_path(storage_path)
        dir_path = FsData.get_path(case_name, virt_path)
        
        if not FsData.is_secure(dir_path, case_name):
            logger.warning(f"Path is not secured: {dir_path}")
            return None
        
        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"Directory not found: {storage_path}")
        
        new_dir = dir_path / name
        if new_dir.exists():
            raise ValueError(f"Directory already exists: {name}")
        
        new_dir.mkdir()
        return DirEntry.from_path(new_dir, case_name)

    @staticmethod
    def download_file(storage_path: str) -> Tuple[bytes, str]:
        """Download a file and return its content and mime type."""
        case_name, virt_path = FsData.get_real_path(storage_path)
        file_path = FsData.get_path(case_name, virt_path)
        
        if not FsData.is_secure(file_path, case_name):
            logger.warning(f"Path is not secured: {file_path}")
            raise ValueError("Path is not secured")
        
        if not file_path.exists():
            raise ValueError(f"File not found: {storage_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {storage_path}")
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        mime_type = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
        return content, mime_type, file_path

    @staticmethod
    def search_files(storage_path: str, filter_expr: Optional[str] = None, deep: bool = False, size_filter: str = 'all') -> List[DirEntry]:
        """Search for files in a directory."""
        case_name, virt_path = FsData.get_real_path(storage_path)
        base_path = FsData.get_path(case_name, virt_path)

        if not FsData.is_secure(base_path, case_name):
            logger.warning(f"Path is not secured: {base_path}")
            raise ValueError("Path is not secured")

        if not base_path.exists() or not base_path.is_dir():
            raise ValueError(f"Path not found or not a directory: {storage_path}")

        results = []

        def matches_filter(file_path: Path, filter_expr: str) -> bool:
            """Check if the file matches the filter (starts with, contains, or equals)."""
            file_name = file_path.name.lower()
            filter_lower = filter_expr.lower()
            return (
                file_name.startswith(filter_lower) or
                filter_lower in file_name or
                file_name == filter_lower
            )

        def matches_size(file_path: Path, size_filter: str) -> bool:
            """Check if the file matches the size filter."""
            file_size = file_path.stat().st_size
            if size_filter == 'small':
                return file_size <= 1024 * 1024
            elif size_filter == 'medium':
                return 1024 * 1024 < file_size <= 10 * 1024 * 1024
            elif size_filter == 'large':
                return file_size > 10 * 1024 * 1024
            else:  # 'all'
                return True

        if deep:
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    file_path = Path(root) / file
                    if filter_expr and not matches_filter(file_path, filter_expr):
                        continue
                    if not matches_size(file_path, size_filter):
                        continue
                    entry = DirEntry.from_path(file_path, case_name)
                    results.append(entry)
        else:
            for item in base_path.iterdir():
                if not item.is_file():
                    continue
                if filter_expr and not matches_filter(item, filter_expr):
                    continue
                if not matches_size(item, size_filter):
                    continue
                entry = DirEntry.from_path(item, case_name)
                results.append(entry)

        return results
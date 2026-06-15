from __future__ import annotations

from typing import Optional, Union
from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_service.postgres.model.OsirDbHandlerModel import OsirDbHandlerModel
from osir_service.postgres.model.OsirDbTaskModel import OsirDbTaskModel
from pydantic import BaseModel, field_validator

"""
==========================================
API Endpoint: GET /api/module
==========================================
Description: Retrieves all of the OSIR module.

Request model:
  - N/A

Response model:
  - GetModuleListResponse

==========================================
"""

# A directory node of the module configuration tree. It simply mirrors the
# filesystem under OSIR/configs/modules: no category name is hardcoded, so
# adding a new directory level or category requires no model change.
class OsirModuleGroupModel(BaseModel):
    modules: list[str] = []
    groups: dict[str, OsirModuleGroupModel] = {}

    @classmethod
    def from_paths(cls, paths: list[str]) -> OsirModuleGroupModel:
        """Builds the tree from the flat list of relative YAML paths
        returned by the IPC (FileManager.all_modules(relative=True))."""
        tree = cls()
        for raw in sorted(paths):
            parts = [p for p in str(raw).replace("\\", "/").strip("/").split("/") if p]
            if not parts:
                continue
            node = tree
            for segment in parts[:-1]:
                child = node.groups.get(segment)
                if child is None:
                    child = cls()
                    node.groups[segment] = child
                node = child
            node.modules.append(parts[-1])
        return tree

    def find(self, *path: str) -> Optional[OsirModuleGroupModel]:
        """Navigates to a subgroup, e.g. find("unix", "live_response")."""
        node = self
        for raw in path:
            for segment in [p for p in str(raw).replace("\\", "/").strip("/").split("/") if p]:
                node = node.groups.get(segment)
                if node is None:
                    return None
        return node


class GetModuleListResponse(OsirIpcResponse):
    response: OsirModuleGroupModel

    @field_validator("response", mode="before")
    @classmethod
    def _build_tree(cls, value):
        # The IPC returns a flat list of relative YAML paths: build the tree.
        if isinstance(value, list):
            return OsirModuleGroupModel.from_paths(value)
        return value

"""
==========================================
API Endpoint: POST /api/module/info
==========================================
Description: Return the OSIR module info if it exists.

Request model:
  - PostModuleInfoRequest

Response model:
  - GetModuleExistsResponse

==========================================
"""


class PostModuleInfoRequest(BaseModel):
    modules: list[str]
    keys: list[str] = ["all"]


class GetModuleExistsResponse(OsirIpcResponse):
    response: Union[None, dict[str, dict]]

"""
==========================================
API Endpoint: POST /api/module/run
==========================================
Description: Run a OSIR module on a case

Request model:
  - PostModuleRunRequest

Response model:
  - PostModuleRunResponse

==========================================
"""


class PostModuleRunRequest(BaseModel):
    module_name: str
    case_name: str
    input_path: Optional[str] = None


class PostModuleRunResponse(OsirIpcResponse):
    response: OsirDbHandlerModel

"""
==========================================
API Endpoint: POST /api/module/run_on_file
==========================================
Description: Run a OSIR module on a case

Request model:
  - PostModuleRunRequest

Response model:
  - PostModuleRunOnFileResponse

==========================================
"""


class PostModuleRunOnFileResponse(OsirIpcResponse):
    response: OsirDbTaskModel

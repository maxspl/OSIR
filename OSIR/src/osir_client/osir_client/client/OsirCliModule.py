import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, PrivateAttr

from osir_lib.logger.logger import AppLogger, CustomLogger
from osir_lib.core.model.OsirModuleModel import OsirModuleModel

from osir_client.client.OsirCliHandler import OsirCliHandler
from osir_client.client.OsirCliDisplay import OsirCliDisplay
from osir_api.api.model.OsirApiModuleModel import GetModuleListResponse, GetModuleExistsResponse, PostModuleRunResponse, PostModuleRunOnFileResponse

logger: CustomLogger = AppLogger().get_logger()

if TYPE_CHECKING:
    from osir_client.client.OsirClient import OsirClient
    from osir_client.client.OsirCliCase import OsirCliCase


class OsirCliModule(BaseModel):
    _api: Optional["OsirClient"] = PrivateAttr(default=None)
    _context: Optional["OsirCliCase"] = PrivateAttr(default=None)

    @property
    def ctx(self) -> "OsirCliCase":
        return self._context

    def exists(self, module_name: str) -> Optional[OsirModuleModel]:
        """
        Retrieve module info by name.
        GET /api/module/{module_name}/info
        """
        response: GetModuleExistsResponse = self._api.get(
            f"/api/module/{module_name}/info",
            response_model=GetModuleExistsResponse
        )
        return response.response

    def list(self, print: bool = True) -> dict:
        """
        Retrieve all available modules.
        GET /api/module
        """
        response: GetModuleListResponse = self._api.get(
            "/api/module",
            response_model=GetModuleListResponse
        )
        if print:
            OsirCliDisplay.modules(response.response)
        return response.response

    def _upload(self, case_name: str, file_path: str) -> str:
        """
            Upload a file to the case and return the server-side matched path.
            POST /api/case/{case_name}/uploads
        """
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        chunk_size = 10 * 1024 * 1024  # 10MB chunks
        total_chunks = max(1, (file_size + chunk_size - 1) // chunk_size)

        logger.info(f"Uploading '{file_name}' in {total_chunks} chunk(s)...")

        with open(file_path, "rb") as f:
            for chunk_number in range(total_chunks):
                chunk_data = f.read(chunk_size)
                files = {"file": (file_name, chunk_data, "application/octet-stream")}
                data = {
                    "name": file_name,
                    "chunk_number": chunk_number,
                    "total_chunks": total_chunks,
                }
                self._api.upload(
                    f"/api/case/{case_name}/uploads",
                    files=files,
                    data=data
                )
                logger.info(f"Chunk {chunk_number + 1}/{total_chunks} uploaded.")

        logger.info(f"Upload complete: '{file_name}'")
        return file_name

    def run(self, module_name: str, input_path: Optional[str] = None) -> OsirCliHandler:
        """
        Run a module against the current case context.
        POST /api/module/{module_name}/run
        """
        if self.ctx is None or self.ctx.name is None:
            logger.error("You can't run a module on a not setup case")
            return self
        try:
            payload = {"case_name": self.ctx.name}

            if input_path:
                if not os.path.exists(input_path):
                    logger.error(f"Input path does not exist: '{input_path}'")
                    return self
                uploaded_name = self._upload(self.ctx.name, input_path)
                uploaded_path = Path("/OSIR/share/cases") / self.ctx.name / "upload" / uploaded_name
                payload["input_path"] = str(uploaded_path)

                response: PostModuleRunOnFileResponse = self._api.post(
                    f"/api/module/{module_name}/run/file",
                    response_model=PostModuleRunOnFileResponse,
                    json=payload
                )
                return response.response

            else:
                response: PostModuleRunResponse = self._api.post(
                    f"/api/module/{module_name}/run",
                    response_model=PostModuleRunResponse,
                    json=payload
                )
                handler = OsirCliHandler(handler_id=str(response.response.handler_id))
                handler._api = self._api
                return handler

        except Exception as e:
            logger.error(f"Failed to run module '{module_name}': {e}")
            return self
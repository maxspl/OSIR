from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse
from osir_lib.core.OsirConstants import OSIR


class OsirException:
    @staticmethod
    def VALIDATION_ERROR(error: str, details: dict = None) -> OsirIpcResponse:
        """Generic validation error."""
        response = {
            "error": f"VALIDATION ERROR: {error}",
            "type": "VALIDATION_ERROR"
        }
        if details:
            response["details"] = details
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=400,
            message=f"Validation error: {error}",
            response=response
        )

    @staticmethod
    def FILE_OPERATION_ERROR(error: str, operation: str = "file operation") -> OsirIpcResponse:
        """Error during file operations."""
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=500,
            message=f"File operation error: {error}",
            response={
                "error": f"{operation.upper()} ERROR: {error}",
                "type": "FILE_OPERATION_ERROR",
                "operation": operation
            }
        )

    @staticmethod
    def FILE_NOT_FOUND(path: str) -> OsirIpcResponse:
        """File or directory not found."""
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=404,
            message=f"File not found: {path}",
            response={
                "error": f"FILE NOT FOUND: {path}",
                "type": "FILE_NOT_FOUND",
                "path": path
            }
        )

    @staticmethod
    def IO_ERROR(error: str) -> OsirIpcResponse:
        """I/O error during file operations."""
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=500,
            message=f"I/O error: {error}",
            response={
                "error": f"IO ERROR: {error}",
                "type": "IO_ERROR"
            }
        )

    @staticmethod
    def MODULE_NOT_FOUND(module: str) -> OsirIpcResponse:
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=500,
            response={
                "error": f"MODULE NOT FOUND: {module}",
                "type": "MODULE_NOT_FOUND"
            }
        )

    @staticmethod
    def MODULE_VALIDATION_ERROR(error: str) -> OsirIpcResponse:
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=500,
            response={
                "error": f"MODULE VALIDATION ERROR: {error}",
                "type": "MODULE_VALIDATION_ERROR"
            }
        )

    @staticmethod
    def MODULE_LOAD_ERROR(error: str) -> OsirIpcResponse:
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=500,
            response={
                "error": f"MODULE LOAD ERROR: {error}",
                "type": "MODULE_LOAD_ERROR"
            }
        )

    @staticmethod
    def UNEXPECTED_ERROR(error: str) -> OsirIpcResponse:
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=500,
            response={
                "error": f"UNEXPECTED ERROR: {error}",
                "type": "UNEXPECTED_ERROR"
            }
        )
    
    @staticmethod
    def UNKNOWN_ACTION(action: str) -> OsirIpcResponse:
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=500,
            response={
                "error": f"Action not found: {action}",
                "type": "ACTION_NOT_FOUND"
            }
        )
    
    @staticmethod
    def CASE_NOT_FOUND(case: str) -> OsirIpcResponse:
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=500,
            response={
                "error": f"CASE NOT FOUND: {case}",
                "type": "CASE_NOT_FOUND"
            }
        )

    @staticmethod
    def MISSING_PARAMETER(parameter_name: str) -> OsirIpcResponse:
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=400,
            response={
                "error": f"MISSING_PARAMETER: '{parameter_name}' is required but was not provided.",
                "type": "MISSING_PARAMETER",
                "details": {
                    "parameter": parameter_name,
                    "hint": "Please ensure all required parameters are included in your request."
                }
            }
        )

    @staticmethod
    def PROFILE_OR_MODULE_REQUIRED() -> OsirIpcResponse:
        """At least one of profile or modules must be specified."""
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=400,
            message="At least one of profile or modules must be specified.",
            response={
                "error": "PROFILE_OR_MODULE_REQUIRED",
                "type": "VALIDATION_ERROR",
                "details": {
                    "hint": "Please provide either a profile or a list of modules."
                }
            }
        )

    @staticmethod
    def PROFILE_REQUIRED_FOR_MODULE_OPERATIONS() -> OsirIpcResponse:
        """modules_to_add or modules_to_remove can only be used when a profile is specified."""
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=400,
            message="Profile is required for module add/remove operations.",
            response={
                "error": "PROFILE_REQUIRED_FOR_MODULE_OPERATIONS",
                "type": "VALIDATION_ERROR",
                "details": {
                    "hint": "modules_to_add and modules_to_remove require a profile to be specified."
                }
            }
        )

    @staticmethod
    def CASE_REQUIRED() -> OsirIpcResponse:
        """case_name is required when using profile or modules."""
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=400,
            message="case_name is required when using profile or modules.",
            response={
                "error": "CASE_REQUIRED",
                "type": "VALIDATION_ERROR",
                "details": {
                    "hint": "Please provide a case_name when specifying profile or modules."
                }
            }
        )

    @staticmethod
    def FILES_OR_FOLDERS_REQUIRED() -> OsirIpcResponse:
        """At least one of files_input or folders_input must be specified."""
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=400,
            message="At least one of files_input or folders_input must be specified.",
            response={
                "error": "FILES_OR_FOLDERS_REQUIRED",
                "type": "VALIDATION_ERROR",
                "details": {
                    "hint": "Please provide either files_input or folders_input."
                }
            }
        )

    @staticmethod
    def MODULE_REQUIRED_FOR_FILES() -> OsirIpcResponse:
        """files_module is required when processing files_input."""
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=400,
            message="files_module is required when processing files_input.",
            response={
                "error": "MODULE_REQUIRED_FOR_FILES",
                "type": "VALIDATION_ERROR",
                "details": {
                    "hint": "Please provide a files_module parameter when specifying files_input."
                }
            }
        )

    @staticmethod
    def MODULE_REQUIRED_FOR_FOLDERS() -> OsirIpcResponse:
        """Either folders_modules or files_in_folder_modules is required when processing folders_input."""
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=400,
            message="Either folders_modules or files_in_folder_modules is required when processing folders_input.",
            response={
                "error": "MODULE_REQUIRED_FOR_FOLDERS",
                "type": "VALIDATION_ERROR",
                "details": {
                    "hint": "Please provide either folders_modules or files_in_folder_modules when specifying folders_input."
                }
            }
        )

    @staticmethod
    def CASE_NAME_REQUIRED() -> OsirIpcResponse:
        """case_name is required for advanced handler creation."""
        return OsirIpcResponse(
            version=OSIR.VERSION,
            status=400,
            message="case_name is required for advanced handler creation.",
            response={
                "error": "CASE_NAME_REQUIRED",
                "type": "VALIDATION_ERROR",
                "details": {
                    "hint": "Please provide a case_name parameter."
                }
            }
        )

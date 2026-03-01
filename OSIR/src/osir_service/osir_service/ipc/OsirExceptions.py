from osir_service.ipc.OsirIpcModel import OsirIpcResponse
from osir_lib.core.OsirConstants import OSIR


class OsirException:
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

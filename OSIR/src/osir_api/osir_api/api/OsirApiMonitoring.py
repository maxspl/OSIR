from fastapi import APIRouter

from osir_api.api.model.OsirApiMonitoringModel import GetSystemMetricsResponse
from osir_api.api.OsirApiExceptions import UnexpectedExceptionResponse

from osir_api.api.OsirIpcCall import OsirIpcCall
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()
router = APIRouter()


@router.get("/system/metrics",
            response_model=GetSystemMetricsResponse,
            responses={500: {"model": UnexpectedExceptionResponse}})
def system_metrics(window_seconds: int = 900):
    """Recent host resource samples (RAM/CPU/load) per agent for the UI graphs."""
    return OsirIpcCall("get_system_metrics", params={"window_seconds": window_seconds})

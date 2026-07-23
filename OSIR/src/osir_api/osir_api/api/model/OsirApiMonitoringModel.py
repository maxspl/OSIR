from typing import List

from osir_service.postgres.model.OsirDbMetricsModel import OsirDbMetricsModel
from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse

"""
==========================================
API Endpoint: GET /api/system/metrics
==========================================
Description: Returns recent host resource samples (RAM/CPU/load) per agent,
             used by the web UI to graph each agent's load over time.

Response model:
  - GetSystemMetricsResponse
"""


class GetSystemMetricsResponse(OsirIpcResponse):
    response: List[OsirDbMetricsModel]

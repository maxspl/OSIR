from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OsirDbMetricsModel(BaseModel):
    """
        A single host resource sample reported by an agent.

        One row per (agent, timestamp). Percentages are 0-100, memory figures
        are in MB. Optional fields tolerate partial samples (e.g. a host with no
        swap, or a psutil call that failed for one metric only).
    """
    agent: str
    ts: datetime
    mem_pct: Optional[float] = None
    mem_used_mb: Optional[float] = None
    mem_total_mb: Optional[float] = None
    swap_pct: Optional[float] = None
    cpu_pct: Optional[float] = None
    loadavg: Optional[float] = None
    worker_rss_mb: Optional[float] = None

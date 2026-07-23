from typing import List, Optional

from osir_lib.logger import AppLogger
from osir_service.postgres.model.OsirDbMetricsModel import OsirDbMetricsModel

logger = AppLogger().get_logger()


class OsirDbMetrics:
    """
        Stores and retrieves host resource samples (RAM/CPU/load) reported by
        agents, used by the web UI to graph the load of each agent over time.

        One row per (agent, timestamp). The table is a short-lived time series:
        rows are pruned past a retention window so it never grows unbounded.
    """

    def __init__(self, db_osir):
        """
            Initializes the OsirDbMetrics with a database connection.
        """
        self.db = db_osir

    def create_table(self):
        """
            Initializes the 'osir_metrics' table and its time-range indexes.
        """
        try:
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS osir_metrics (
                    id             BIGSERIAL PRIMARY KEY,
                    agent          TEXT NOT NULL,
                    ts             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    mem_pct        REAL,
                    mem_used_mb    REAL,
                    mem_total_mb   REAL,
                    swap_pct       REAL,
                    cpu_pct        REAL,
                    loadavg        REAL,
                    worker_rss_mb  REAL
                );
            """)
            self.db.execute_query(
                "CREATE INDEX IF NOT EXISTS idx_osir_metrics_ts ON osir_metrics (ts)"
            )
            self.db.execute_query(
                "CREATE INDEX IF NOT EXISTS idx_osir_metrics_agent_ts "
                "ON osir_metrics (agent, ts)"
            )
        except Exception as e:
            logger.error(f"Error creating `osir_metrics` table: {e}")
            raise

    def insert(
        self,
        agent: str,
        mem_pct: Optional[float] = None,
        mem_used_mb: Optional[float] = None,
        mem_total_mb: Optional[float] = None,
        swap_pct: Optional[float] = None,
        cpu_pct: Optional[float] = None,
        loadavg: Optional[float] = None,
        worker_rss_mb: Optional[float] = None,
    ) -> None:
        """
            Records a single host resource sample for an agent.

            Args:
                agent (str): The reporting agent's hostname.
                mem_pct (float, optional): Used RAM as a percentage (0-100).
                mem_used_mb (float, optional): Used RAM in MB.
                mem_total_mb (float, optional): Total RAM in MB.
                swap_pct (float, optional): Used swap as a percentage (0-100).
                cpu_pct (float, optional): CPU usage as a percentage (0-100).
                loadavg (float, optional): 1-minute load average.
                worker_rss_mb (float, optional): Resident memory of the agent's
                    worker processes in MB.

            Raises:
                Exception: If the insert query fails.
        """
        try:
            self.db.execute_query(
                """
                INSERT INTO osir_metrics (
                    agent, mem_pct, mem_used_mb, mem_total_mb,
                    swap_pct, cpu_pct, loadavg, worker_rss_mb
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (agent, mem_pct, mem_used_mb, mem_total_mb,
                 swap_pct, cpu_pct, loadavg, worker_rss_mb),
            )
        except Exception as e:
            logger.error(f"Error inserting metrics sample for {agent}: {e}")
            raise

    def list_recent(
        self,
        window_seconds: int = 900,
        agent: Optional[str] = None,
    ) -> List[OsirDbMetricsModel]:
        """
            Retrieves samples from the last ``window_seconds``, oldest first.

            Args:
                window_seconds (int): Size of the time window to return.
                agent (str, optional): Restrict to a single agent's samples.

            Returns:
                List[OsirDbMetricsModel]: Samples ordered by timestamp ascending
                    (chart-ready), across all agents unless one is given.

            Raises:
                Exception: If the query fails.
        """
        try:
            query = (
                "SELECT agent, ts, mem_pct, mem_used_mb, mem_total_mb, "
                "swap_pct, cpu_pct, loadavg, worker_rss_mb "
                "FROM osir_metrics "
                "WHERE ts >= NOW() - (%s * INTERVAL '1 second')"
            )
            params = [window_seconds]
            if agent:
                query += " AND agent = %s"
                params.append(agent)
            query += " ORDER BY ts ASC"

            rows = self.db.execute_query(query, params, fetch="fetchall")
            return [OsirDbMetricsModel.model_validate(dict(x)) for x in (rows or [])]
        except Exception as e:
            logger.error(f"Error fetching recent metrics: {e}")
            raise

    def prune(self, max_age_seconds: int = 86400) -> None:
        """
            Deletes samples older than ``max_age_seconds`` to bound table size.

            Args:
                max_age_seconds (int): Retention window; older rows are removed.

            Raises:
                Exception: If the delete query fails.
        """
        try:
            self.db.execute_query(
                "DELETE FROM osir_metrics WHERE ts < NOW() - (%s * INTERVAL '1 second')",
                (max_age_seconds,),
            )
        except Exception as e:
            logger.error(f"Error pruning metrics: {e}")
            raise

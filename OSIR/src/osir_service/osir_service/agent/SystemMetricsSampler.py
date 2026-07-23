import os
import time
from threading import Thread, Event

import psutil

from osir_lib.logger import AppLogger
from osir_service.postgres.OsirDb import OsirDb

logger = AppLogger().get_logger()


class SystemMetricsSampler:
    """
        Periodically samples this host's resource usage (RAM/CPU/load) and
        records it into the 'osir_metrics' table, so the web UI can graph the
        load of each agent over time.

        One sampler runs per agent, in the worker parent process. It also owns
        pruning of old rows so the time-series table stays bounded. Every call
        is best-effort: a sampling or DB error is logged and skipped, never
        raised, so it cannot take the agent down.
    """

    def __init__(
        self,
        agent: str,
        interval: int = 10,
        retention_seconds: int = 86400,
        prune_every: int = 300,
    ):
        """
            Args:
                agent (str): Hostname used to tag this agent's samples.
                interval (int): Seconds between samples.
                retention_seconds (int): Age past which rows are pruned.
                prune_every (int): Seconds between prune passes.
        """
        self.agent = agent
        self.interval = max(1, interval)
        self.retention_seconds = retention_seconds
        self.prune_every = prune_every
        self._stop = Event()
        self._thread = None

    @classmethod
    def from_env(cls, agent: str) -> "SystemMetricsSampler":
        """
            Builds a sampler from OSIR_METRICS_* env vars, with safe defaults.

            Args:
                agent (str): Hostname used to tag this agent's samples.

            Returns:
                SystemMetricsSampler: A configured, not-yet-started sampler.
        """
        def _int(name, default):
            try:
                return int(os.getenv(name, default))
            except (TypeError, ValueError):
                return default

        return cls(
            agent=agent,
            interval=_int("OSIR_METRICS_INTERVAL", 10),
            retention_seconds=_int("OSIR_METRICS_RETENTION", 86400),
        )

    def start(self) -> None:
        """Starts the sampling thread (daemon). No-op if already running."""
        if self._thread and self._thread.is_alive():
            return
        self._thread = Thread(target=self._run, name="metrics-sampler", daemon=True)
        self._thread.start()
        logger.info(
            f"System metrics sampler started for agent '{self.agent}' "
            f"(interval={self.interval}s, retention={self.retention_seconds}s)"
        )

    def stop(self) -> None:
        """Signals the sampling thread to stop and waits briefly for it."""
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.interval + 2)

    def _worker_rss_mb(self) -> float:
        """
            Sums the resident memory of this process and its worker children.

            The Celery workers are multiprocessing children of the parent that
            runs the sampler, so children(recursive=True) covers them.

            Returns:
                float: Total resident memory of the agent's processes, in MB.
        """
        try:
            proc = psutil.Process(os.getpid())
            procs = [proc] + proc.children(recursive=True)
            total = 0
            for p in procs:
                try:
                    total += p.memory_info().rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return total / (1024 * 1024)
        except Exception:
            return None

    def _sample_once(self) -> None:
        """Takes one sample and writes it. Best-effort; errors are logged."""
        try:
            vm = psutil.virtual_memory()
            sm = psutil.swap_memory()
            # interval=None -> non-blocking, delta since the previous call.
            cpu = psutil.cpu_percent(interval=None)
            try:
                load1 = os.getloadavg()[0]
            except (OSError, AttributeError):
                load1 = None

            with OsirDb() as db:
                db.metrics.insert(
                    agent=self.agent,
                    mem_pct=vm.percent,
                    mem_used_mb=(vm.total - vm.available) / (1024 * 1024),
                    mem_total_mb=vm.total / (1024 * 1024),
                    swap_pct=sm.percent,
                    cpu_pct=cpu,
                    loadavg=load1,
                    worker_rss_mb=self._worker_rss_mb(),
                )
        except Exception as e:
            logger.error(f"Metrics sampling failed for {self.agent}: {e}")

    def _run(self) -> None:
        """Sampling loop: sample every interval, prune every prune_every."""
        # Prime cpu_percent so the first real sample reflects a delta, not 0.
        try:
            psutil.cpu_percent(interval=None)
        except Exception:
            pass

        last_prune = 0.0
        while not self._stop.is_set():
            self._sample_once()

            now = time.monotonic()
            if now - last_prune >= self.prune_every:
                try:
                    with OsirDb() as db:
                        db.metrics.prune(self.retention_seconds)
                except Exception as e:
                    logger.error(f"Metrics prune failed: {e}")
                last_prune = now

            self._stop.wait(self.interval)

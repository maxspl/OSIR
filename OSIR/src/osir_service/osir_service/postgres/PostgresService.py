from psycopg2 import pool, OperationalError, InterfaceError
from osir_service.postgres.task_manager import TaskManager
from osir_service.postgres.handler_manager import HandlerManager
from osir_service.postgres.case_manager import CaseManager
from osir_lib.core.FileManager import FileManager
from osir_lib.logger import AppLogger
from osir_lib.core.OsirAgentConfig import OsirAgentConfig
import os
import time
import psycopg2
from psycopg2 import sql
import psycopg2.extras
from psycopg2 import pool
from osir_service.postgres.snapshot_manager import SnapshotManager
psycopg2.extras.register_uuid()


logger = AppLogger().get_logger()


class DbOSIR:
    def __init__(self, host=None, module_name=None, dbname='OSIR_db', port=5432):
        """"
            Central PostgreSQL service for the OSIR framework.
        """
        if host is None:
            try:
                agent_config = OsirAgentConfig()
                host = "host.docker.internal" if agent_config.standalone else agent_config.master_host
            except FileNotFoundError:
                # agent.yml missing -> happens if master launched before agent is installed
                host = "master-postgres"
        self.host = host
        self.dbname = dbname
        self.port = port
        self.user = os.getenv('POSTGRES_USER', 'missing POSTGRES_USER env var')
        self.password = os.getenv('POSTGRES_PASSWORD', 'missing POSTGRES_PASSWORD env var')
        self.host_hostname = os.getenv('HOST_HOSTNAME', 'missing HOST_HOSTNAME env var')  # Default to '%h' if the env var is not set

        self.conn = None
        self._ensure_connection()
        self.module = module_name

        self.case = CaseManager(self)
        self.handler = HandlerManager(self)
        self.task = TaskManager(self)
        self.snapshot = SnapshotManager(self)

        self.snapshot.create_table()
        self.task.create_table()
        self.handler.create_table()
        self.case.create_table()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def _ensure_connection(self):
        """Checks if connection is alive; if not, creates a new one."""
        try:
            # Check if conn exists and is healthy
            if self.conn is None or self.conn.closed != 0:
                logger.info("Connecting to PostgreSQL...")
                self.conn = psycopg2.connect(
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port
                )
                self.conn.autocommit = True
                logger.info("Database connection established.")
            return self.conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.conn = None
            return None

    def execute_query(self, query, params=None, fetch=None, max_retries=5):
        """Executes a query with automatic reconnection and retry logic."""
        last_exception = None

        for attempt in range(max_retries):
            try:
                # 1. Ensure we have a working connection
                conn = self._ensure_connection()
                if not conn:
                    raise OperationalError("Could not establish a database connection.")

                # 2. Execute the query
                with conn.cursor() as cur:
                    cur.execute(query, params)

                    if cur.description is None:
                        return True

                    if fetch == "fetchone":
                        return cur.fetchone()
                    if fetch == "fetchall":
                        return cur.fetchall()
                    return True

            except (OperationalError, InterfaceError) as e:
                last_exception = e
                logger.warning(f"Connection lost (Attempt {attempt + 1}/{max_retries}): {e}")

                # Force a reset of the connection object so the next loop reconnects
                if self.conn:
                    try:
                        self.conn.close()
                    except:
                        pass
                self.conn = None

                # Exponential backoff (2s, 4s, 8s...)
                time.sleep(2 ** attempt)
                continue

            except Exception as e:
                # Permanent SQL errors (syntax, etc.) should not retry
                logger.error(f"SQL Execution Error: {e}")
                raise e

        # If we get here, all retries failed
        logger.error(f"Query permanently failed after {max_retries} attempts.")
        raise last_exception

    def close(self):
        """Cleanly close the connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")

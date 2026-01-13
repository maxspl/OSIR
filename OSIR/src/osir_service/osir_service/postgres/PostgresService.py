from sqlite3 import InterfaceError, OperationalError
import time
from typing import Union
import uuid
import psycopg2
from psycopg2 import sql
import psycopg2.extras
from psycopg2 import pool
from osir_service.postgres.snapshot_manager import SnapshotManager
psycopg2.extras.register_uuid()

import datetime
import os

from osir_lib.core.OsirAgentConfig import OsirAgentConfig
from osir_lib.core.OsirSingleton import singleton
from osir_lib.core.OsirModule import OsirModule
from osir_service.postgres.PostgresConstants import ProcessingStatus
from osir_lib.logger import AppLogger
from osir_service.postgres.case_manager import CaseManager
from osir_service.postgres.handler_manager import HandlerManager
from osir_service.postgres.task_manager import TaskManager
from osir_service.postgres.utils import UtilsManager

logger = AppLogger().get_logger()

@singleton
class DbOSIR:
    def __init__(self, host=None, module_name=None, dbname='OSIR_db', port=5432):
        """
        Initialize the DbOSIR class, connecting to the database and creating necessary tables.

        Args:
            host (str): The database host.
            module_name (str, optional): The module name. Defaults to None.
            dbname (str, optional): The database name. Defaults to 'OSIR_db'.
            port (int, optional): The database port. Defaults to 5432.
        """
        if host is None:
            agent_config = OsirAgentConfig()
            if agent_config.standalone:
                # host = "master-postgres"
                host = "host.docker.internal"
            else:
                host = agent_config.master_host
        self.host = host
        self.dbname = dbname
        self.port = port
        self.user = os.getenv('POSTGRES_USER', 'missing POSTGRES_USER env var')
        self.password = os.getenv('POSTGRES_PASSWORD', 'missing POSTGRES_PASSWORD env var')

        self._init_pool()
        self.module = module_name
        self.host_hostname = os.getenv('HOST_HOSTNAME', 'missing HOST_HOSTNAME env var')  # Default to '%h' if the env var is not set

        self.case = CaseManager(self)
        self.handler = HandlerManager(self)
        self.task = TaskManager(self)
        self.utils = UtilsManager(self)
        self.snapshot = SnapshotManager(self)
        
        if module_name and module_name == "master_status":
            self._create_table_master_status("master_status")
        elif module_name and module_name != "master_status":
            self.create_table_processing_status(module_name)

        self._create_case_snapshot_table()
        self.task.create_table()
        self.handler.create_table()
        self.case.create_table()

    def _init_pool(self):
        """Initialise le pool de connexions."""
        try:
            self.connection_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            logger.info("Connection pool created successfully.")
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise

    def close(self):
        self.cur.close()
        self.conn.close()

    def _connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.conn.autocommit = True
            self.cur = self.conn.cursor()
            logger.info("Connected to the database successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to the database: {e}")
            raise
    
    def execute_query(self, query, params=None, fetch=None, max_retries=3):
        last_exception = None
        
        for attempt in range(max_retries):
            conn = None
            try:
                conn = self.connection_pool.getconn()
                
                # Vérification de santé de la connexion
                if conn.closed != 0:
                    self.connection_pool.putconn(conn, close=True)
                    conn = self.connection_pool.getconn()

                conn.autocommit = True 
                
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    
                    # Si la requête ne retourne pas de données (INSERT, UPDATE, etc.)
                    if cur.description is None:
                        return True
                    
                    # Si on a demandé des données, on respecte le format attendu
                    if fetch == "fetchone":
                        return cur.fetchone()  # Retourne un tuple ou None
                    if fetch == "fetchall":
                        return cur.fetchall()  # Retourne une liste de tuples

                    # Par défaut, si fetch n'est pas précisé mais qu'il y a des données
                    return cur
                    
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
                last_exception = e
                logger.warning(f"DB Issue (attempt {attempt + 1}): {e}")
                if conn:
                    self.connection_pool.putconn(conn, close=True)
                    conn = None
                time.sleep(2 ** attempt)
                continue
            except Exception as e:
                logger.error(f"SQL Error: {e}")
                raise
            finally:
                if conn:
                    self.connection_pool.putconn(conn)
        
        raise last_exception

    def _create_table_master_status(self, table_name):
        try:
            self.execute_query(f"""
                CREATE TABLE IF NOT EXISTS %s (
                    id SERIAL PRIMARY KEY,
                    case_uuid TEXT,
                    case_path TEXT,
                    agent TEXT,
                    input_file TEXT,
                    input_dir TEXT,
                    output_file TEXT,
                    output_dir TEXT,
                    output_prefix TEXT,
                    processing_status TEXT,
                    timestamp TIMESTAMPTZ DEFAULT NOW()
                )
            """,(table_name,))

        except Exception as e:
            logger.error(f"Error creating table: {e}")
            raise

    def create_table_processing_status(self, table_name):
        try:
            self.execute_query(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    case_uuid TEXT,
                    case_path TEXT,
                    agent TEXT,
                    input_file TEXT,
                    input_dir TEXT,
                    output_file TEXT,
                    output_dir TEXT,
                    output_prefix TEXT,
                    processing_status TEXT,
                    timestamp TIMESTAMPTZ DEFAULT NOW()
                )
            """)
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            raise

    def _create_case_snapshot_table(self):
        query = """
            CREATE TABLE IF NOT EXISTS case_snapshot (
                case_uuid TEXT NOT NULL,
                case_path TEXT NOT NULL,
                path TEXT NOT NULL,
                entry_type TEXT NOT NULL,
                PRIMARY KEY (case_uuid, path)
            )
            """
        try:
            self.execute_query(query)
            logger.debug("Table `case_snapshot` ensured.")
        except Exception as e:
            logger.error(f"Error creating `case_snapshot` table: {str(e)}")
            self.conn.rollback()

OSIR_DB = DbOSIR()
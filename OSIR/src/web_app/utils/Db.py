from sqlalchemy import create_engine
import os


class Db_accessor:
    def __init__(self):
        # Database connection details
        self.db_user = os.getenv('POSTGRES_USER', 'missing POSTGRES_USER env var')
        self.db_password = os.getenv('POSTGRES_PASSWORD', 'missing POSTGRES_PASSWORD env var')
        self.db_host = 'postgres'
        self.db_port = '5432'
        self.db_name = 'OSIR_db'

        # Connection string
        self.conn_str = f'postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'
        self.engine = create_engine(self.conn_str)

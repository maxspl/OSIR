from sqlalchemy import create_engine


class Db_accessor:
    def __init__(self):
        # Database connection details
        self.db_user = 'dfir'
        self.db_password = 'dfir'
        self.db_host = 'postgres'
        self.db_port = '5432'
        self.db_name = 'OSIR_db'

        # Connection string
        self.conn_str = f'postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'
        self.engine = create_engine(self.conn_str)

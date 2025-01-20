import psycopg2
from psycopg2 import sql
import datetime
import os
from src.log.logger_config import AppLogger
from src.utils.BaseModule import BaseModule

logger = AppLogger(__name__).get_logger()


class DbOSIR:
    def __init__(self, host, case_path=None, module_name=None, dbname='OSIR_db', user='dfir', password='dfir', port=5432):
        """
        Initialize the DbOSIR class, connecting to the database and creating necessary tables.

        Args:
            host (str): The database host.
            case_path (str, optional): The case path. Defaults to None.
            module_name (str, optional): The module name. Defaults to None.
            dbname (str, optional): The database name. Defaults to 'OSIR_db'.
            user (str, optional): The database user. Defaults to 'dfir'.
            password (str, optional): The database password. Defaults to 'dfir'.
            port (int, optional): The database port. Defaults to 5432.
        """
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.conn.autocommit = True  # Enable autocommit mode
        self.cur = self.conn.cursor()
        self.module = module_name
        self.host_hostname = os.getenv('HOST_HOSTNAME', 'missing HOST_HOSTNAME env var')  # Default to '%h' if the env var is not set
        if module_name and module_name == "master_status":
            self._create_table_master_status("master_status")
        elif module_name and module_name != "master_status":
            self.create_table_processing_status(module_name)
        self._create_case_snapshot_table()  # Create table used for case snapshot

    def create_table_processing_status(self, table_name):
        """
        Create a table for processing status if it doesn't exist.

        Args:
            table_name (str): The name of the table to create.
        """
        self.cur.execute(f"""
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
        self.conn.commit()

    def _create_table_master_status(self, table_name):
        """
        Create the master status table if it doesn't exist.

        Args:
            table_name (str): The name of the table to create.
        """
        self.cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                case_path TEXT,
                status TEXT,
                case_uuid TEXT,
                modules_selected TEXT,
                timestamp TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        self.conn.commit()

    def store_data(self, case_path, module: BaseModule, status, case_uuid):
        """
        Store data into the specified module's table.

        Args:
            case_path (str): The case path.
            module (BaseModule): The module instance containing data to store.
            status (str): The processing status.
            case_uuid (str): The case UUID.
        """
        # Extracting values from module instance
        input_file = module.input.file
        input_dir = module.input.dir
        output_file = module.output.output_file
        output_dir = module.output.output_dir
        output_prefix = module.output.output_prefix
        
        # SQL statement with placeholders for each column
        self.cur.execute(f"""
            INSERT INTO {module.module_name} (
                case_uuid, 
                case_path,
                agent,
                input_file, 
                input_dir, 
                output_file, 
                output_dir, 
                output_prefix, 
                processing_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(case_uuid), 
            case_path,
            self.host_hostname, 
            input_file, 
            input_dir, 
            output_file, 
            output_dir, 
            output_prefix, 
            status
        )
        )
        self.conn.commit()

    def update_record(self, module: BaseModule, status, case_uuid):
        """
        Update an existing record in the specified module's table.

        Args:
            module (BaseModule): The module instance containing data to update.
            status (str): The processing status.
            case_uuid (str): The case UUID.
        """
        try:
            # Extracting values from module instance
            input_file = module.input.file
            input_dir = module.input.dir
            output_file = module.output.output_file
            output_dir = module.output.output_dir
            output_prefix = module.output.output_prefix
            
            # Create the SET part of the SQL query dynamically
            update_data = {
                "agent": self.host_hostname,
                "input_file": input_file,
                "input_dir": input_dir,
                "output_file": output_file,
                "output_dir": output_dir,
                "output_prefix": output_prefix,
                "processing_status": status
            }
            
            set_clause = ', '.join([f"{col} = %s" for col in update_data.keys()])
            values = list(update_data.values())

            # Add values for the WHERE clause
            values.append(case_uuid)

            # Define the SQL UPDATE query
            
            update_query = f"""
            UPDATE {module.module_name}
            SET {set_clause}
            WHERE case_uuid = %s
                AND ((input_file != '' AND input_file = %s)
                OR (input_dir != '' AND input_dir = %s))
            """

            # Execute the SQL query with the correct values order
            self.cur.execute(update_query, values + [input_file, input_dir])

            # Commit the changes
            self.conn.commit()

            # Check if the record was updated
            rows_updated = self.cur.rowcount
            logger.debug(f"Database updates {rows_updated} record(s).")

        except Exception as error:
            logger.error(f"Error updating record: {error}")
        
    def store_master_status(self, case_path, status, case_uuid, modules_selected):
        """
        Store or update the master status for a given case.

        Args:
            case_path (str): The case path.
            status (str): The processing status.
            case_uuid (str): The case UUID.
            modules_selected (str): The selected modules.
        """
        current_timestamp = datetime.datetime.now()
        try:
            # Check if the record exists
            self.cur.execute("""
                SELECT 1 FROM master_status WHERE case_path = %s
            """, (case_path,))
            exists = self.cur.fetchone()

            if exists:
                # Record exists, update it
                self.cur.execute("""
                    UPDATE master_status
                    SET status = %s, case_uuid = %s, timestamp = %s, modules_selected = %s
                    WHERE case_path = %s
                """, (status, case_uuid, current_timestamp, modules_selected, case_path))
            else:
                # Record does not exist, insert new one
                self.cur.execute("""
                    INSERT INTO master_status (case_path, status, case_uuid, modules_selected)
                    VALUES (%s, %s, %s, %s)
                """, (case_path, status, case_uuid, modules_selected))

            # Commit the changes
            self.conn.commit()

            # Log the result
            action = "Updated" if exists else "Inserted"
            logger.debug(f"{action} master_status record for case_path: {case_path}")

        except Exception as error:
            logger.error(f"Error in add_or_update_master_status: {error}")
            self.conn.rollback()
            
    def close(self):
        """
        Close the database connection.
        """
        self.cur.close()
        self.conn.close()
        
    def check_input_file(self, case_uuid, input_file):
        try:
            """
            Checks if the specified input file is currently being processed in any table except 'master_status' and 'case_snapshot'.

            Args:
                case_uuid (str): The UUID of the case.
                input_file (str): The path of the input file to check.

            Returns:
                bool: True if the input file is currently being processed, False otherwise.
            """
            # Query to check if the input_file exists with processing_status not as "processing_done"
            query = sql.SQL("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public' AND table_name != 'master_status' AND table_name != 'case_snapshot'
            """)
            self.cur.execute(query)
            tables = self.cur.fetchall()

            for table in tables:
                query = sql.SQL("""
                    SELECT 1
                    FROM {}
                    WHERE case_uuid = %s AND input_file = %s AND processing_status = 'processing_started'
                    LIMIT 1
                """).format(sql.Identifier(table[0]))
                self.cur.execute(query, (case_uuid, input_file))
                if self.cur.fetchone():
                    logger.debug(f"Query: {self.cur.mogrify(query, (case_uuid, input_file))}")
                    return True
            
            return False

        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return False
        
    def check_input_dir(self, case_uuid, input_dir):
        """
        Checks if the specified input directory or its sub-items are currently being processed in any table except 'master_status'.
        Following table are excluded : 'processing_done', 'case_snapshot'
        Args:
            case_uuid (str): The UUID of the case.
            input_dir (str): The path of the input directory to check.

        Returns:
            bool: True if the input directory or its sub-items are currently being processed, False otherwise.
        """
        try:
            # Query to check if the input_dir exists or is a sub item with processing_status not as "processing_done"
            query = sql.SQL("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public' AND table_name != 'master_status' AND table_name != 'case_snapshot'
            """)
            self.cur.execute(query)
            tables = self.cur.fetchall()

            for table in tables:
                query = sql.SQL("""
                    SELECT 1
                    FROM {}
                    WHERE case_uuid = %s AND (
                        input_dir = %s OR input_dir LIKE %s OR input_file LIKE %s
                    ) AND processing_status = 'processing_started'
                    LIMIT 1
                """).format(sql.Identifier(table[0]))
                self.cur.execute(query, (case_uuid, input_dir, f'{input_dir}%', f'{input_dir}%'))
                if self.cur.fetchone():
                    return True
            
            return False

        except Exception as e:
            print(f"Error: {e}")
            return False
        
    def is_processing_active(self, case_uuid):
        """
        Check if there is at least one table with a row for the given case_uuid
        that has a column processing_status not equal to 'processing_done'.
        Following table are excluded : 'processing_done', 'case_snapshot'

        Args:
            case_uuid (str): The case UUID.

        Returns:
            bool: True if such a row exists, False otherwise.
        """
        try:
            query = sql.SQL("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name != 'master_status' AND table_name != 'case_snapshot'
            """)
            self.cur.execute(query)
            tables = self.cur.fetchall()

            for table in tables:
                query = sql.SQL("""
                    SELECT 1
                    FROM {}
                    WHERE case_uuid = %s AND processing_status != 'processing_done'
                    LIMIT 1
                """).format(sql.Identifier(table[0]))
                self.cur.execute(query, (case_uuid,))
                if self.cur.fetchone():
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking processing status: {str(e)}")
            return False
            
    def _create_case_snapshot_table(self):
        """
        Ensure the `case_snapshot` table exists in the database.
        """
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
            self.cur.execute(query)
            self.conn.commit()
            logger.debug("Table `case_snapshot` ensured.")
        except Exception as e:
            logger.error(f"Error creating `case_snapshot` table: {str(e)}")
            self.conn.rollback()

    def get_stored_case_snapshot(self, case_path):
        """
        Retrieve stored directory entries for the specified case UUID.

        Args:
            case_path (str): The path of the case.

        Returns:
            list: A list of (path, entry_type) tuples.
        """
        query = """
        SELECT path, entry_type
        FROM case_snapshot
        WHERE case_path = %s
        """
        try:
            self.cur.execute(query, (case_path,))
            rows = self.cur.fetchall()
            logger.debug(f"Retrieved {len(rows)} entries for case_path: {case_path}")
            return [(row[0], row[1]) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching entries for case_path {case_path}: {str(e)}")
            return []

    def store_case_snapshot(self, case_uuid, case_path, entries_list):
        import io
        try:
            # 1) Delete old entries first
            delete_query = "DELETE FROM case_snapshot WHERE case_uuid = %s"
            self.cur.execute(delete_query, (case_uuid,))
            # 2) Prepare data as CSV format in memory
            output = io.StringIO()
            for path, entry_type in entries_list:
                if '\\' in path:
                    logger.warning(f"Skipping entry due to invalid backslash: path={path}, entry_type={entry_type}")
                    continue
                output.write(f"{case_uuid}\t{case_path}\t{path}\t{entry_type}\n")
            output.seek(0)  # Move cursor back to start

            # 3) Use copy_from to bulk-insert
            self.cur.copy_from(
                file=output,
                table='case_snapshot',
                columns=('case_uuid', 'case_path', 'path', 'entry_type'),
                null=''  # specify how to handle NULL if needed
            )

            # 4) Commit changes
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Bulk insert error for case_uuid {case_uuid}: {str(e)}")
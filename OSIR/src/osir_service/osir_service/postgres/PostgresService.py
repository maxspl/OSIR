from typing import Union
import uuid
import psycopg2
from psycopg2 import sql
import psycopg2.extras

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

logger = AppLogger(__name__).get_logger()

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
        user = os.getenv('POSTGRES_USER', 'missing POSTGRES_USER env var')
        password = os.getenv('POSTGRES_PASSWORD', 'missing POSTGRES_PASSWORD env var')
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.conn.autocommit = True  # Enable autocommit mode
        self.cur = self.conn.cursor()
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

    def close(self):
        self.cur.close()
        self.conn.close()

    def _create_table_master_status(self, table_name):
        try:
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
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            raise

    def create_table_processing_status(self, table_name):
        try:
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
            self.cur.execute(query)
            self.conn.commit()
            logger.debug("Table `case_snapshot` ensured.")
        except Exception as e:
            logger.error(f"Error creating `case_snapshot` table: {str(e)}")
            self.conn.rollback()

    # def append_task_ids(
    #     self,
    #     handler_id: str,
    #     new_task_ids: list
    # ) -> bool:
    #     """
    #     Ajoute des identifiants de tâches (`task_id`) à la liste existante dans la table `osir_handlers`.

    #     Args:
    #         handler_id (str): L'UUID du handler à mettre à jour.
    #         new_task_ids (list): Liste des nouveaux UUIDs de tâches à ajouter.

    #     Returns:
    #         bool: True si la mise à jour a réussi, False en cas d'erreur.
    #     """
    #     try:
    #         # Récupérer la liste actuelle des task_ids
    #         self.cur.execute("""
    #             SELECT task_id FROM osir_handlers WHERE handler_id = %s
    #         """, (str(handler_id),))

    #         result = self.cur.fetchone()
    #         if result is None:
    #             logger.error(f"Aucun handler trouvé avec l'ID {handler_id}.")
    #             return False

    #         current_task_ids = result[0] or []

    #         # Si current_task_ids est une chaîne, le convertir en liste
    #         if isinstance(current_task_ids, str):
    #             current_task_ids = [current_task_ids]

    #         # Convertir les UUIDs en chaînes si nécessaire
    #         updated_task_ids = list(set(current_task_ids + [str(task_id) for task_id in new_task_ids]))

    #         # Mettre à jour la liste des task_ids
    #         self.cur.execute("""
    #             UPDATE osir_handlers
    #             SET task_id = %s
    #             WHERE handler_id = %s
    #         """, (updated_task_ids, str(handler_id)))


    #         self.conn.commit()
    #         logger.debug(f"Liste des task_ids pour le handler {handler_id} mise à jour avec succès.")
    #         return True

    #     except Exception as e:
    #         self.conn.rollback()
    #         logger.error(f"Erreur lors de la mise à jour des task_ids pour le handler {handler_id}: {e}")
    #         raise

    # def update_handler_status(
    #     self,
    #     handler_id: str,
    #     status: str
    # ) -> bool:
    #     """
    #     Met à jour le statut (`processing_status`) d'un handler dans la table `osir_handlers`.

    #     Args:
    #         handler_id (str): L'UUID du handler à mettre à jour.
    #         status (str): Le nouveau statut (par exemple, 'processing_started', 'completed', etc.).

    #     Returns:
    #         bool: True si la mise à jour a réussi, False en cas d'erreur.
    #     """
    #     try:
    #         self.cur.execute("""
    #             UPDATE osir_handlers
    #             SET processing_status = %s
    #             WHERE handler_id = %s
    #         """, (status, str(handler_id)))

    #         self.conn.commit()
    #         logger.debug(f"Statut du handler {handler_id} mis à jour avec succès.")
    #         return True

    #     except Exception as e:
    #         self.conn.rollback()
    #         logger.error(f"Erreur lors de la mise à jour du statut du handler {handler_id}: {e}")
    #         raise
    
    # def create_table_osir_case(self):
    #     try:
    #         self.cur.execute("""
    #             CREATE TABLE IF NOT EXISTS osir_case (
    #                 case_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    #                 name TEXT NOT NULL
    #             )
    #         """)
    #         self.conn.commit()
    #     except Exception as e:
    #         logger.error(f"Error creating table osir_case: {e}")
    #         raise
    
    # def create_case(self, name):
    #     try:
    #         # Génère un UUID pour le case
    #         case_uuid = uuid.uuid4()

    #         # Exécute la requête pour insérer le case dans la table
    #         self.cur.execute("""
    #             INSERT INTO osir_case (case_uuid, name)
    #             VALUES (%s, %s)
    #         """, (case_uuid, name))

    #         self.conn.commit()
    #         return case_uuid
    #     except Exception as e:
    #         logger.error(f"Error creating case: {e}")
    #         raise
    
    # def get_case_uuid(self, name=None, case_uuid=None):
    #     try:
    #         if case_uuid:
    #             # Si un UUID est fourni, vérifie s'il existe dans la table
    #             self.cur.execute("""
    #                 SELECT case_uuid FROM osir_case
    #                 WHERE case_uuid = %s
    #             """, (case_uuid,))
    #         elif name:
    #             # Si un nom est fourni, récupère l'UUID correspondant
    #             self.cur.execute("""
    #                 SELECT case_uuid FROM osir_case
    #                 WHERE name = %s
    #             """, (name,))
    #         else:
    #             raise ValueError("Soit un nom, soit un UUID doit être fourni.")

    #         result = self.cur.fetchone()
    #         if result:
    #             return result[0]
    #         else:
    #             return None
    #     except Exception as e:
    #         logger.error(f"Error fetching case UUID: {e}")
    #         raise

    # def create_table_tasks(self):
    #     try:
    #         # Check if the processing_status_enum type already exists
    #         self.cur.execute("""
    #             SELECT 1 FROM pg_type WHERE typname = 'processing_status_enum'
    #         """)
    #         type_exists = self.cur.fetchone() is not None

    #         if not type_exists:
    #             self.cur.execute(f"""
    #                 CREATE TYPE processing_status_enum AS ENUM (
    #                     'task_created',
    #                     'processing_started',
    #                     'processing_done',
    #                     'processing_failed'
    #                 );
    #             """)

    #         self.cur.execute(f"""       
    #             CREATE TABLE IF NOT EXISTS osir_tasks (
    #                 task_id UUID PRIMARY KEY,
    #                 case_uuid TEXT,
    #                 agent TEXT,
    #                 module TEXT,
    #                 input TEXT,
    #                 processing_status processing_status_enum DEFAULT 'task_created',
    #                 timestamp TIMESTAMPTZ DEFAULT NOW()
    #             )
    #         """)
    #         self.conn.commit()
    #     except Exception as e:
    #         logger.error(f"Error creating table: {e}")
    #         raise
    
    # def create_task(
    #     self,
    #     task_id: Union[str, uuid.UUID, None] = None,
    #     case_uuid: str = None,
    #     agent: str = None,
    #     module: str = None,
    #     input: str = None
    # ) -> str:
    #     """
    #     Creates a new task in the `osir_tasks` table with a UUID task_id.

    #     Args:
    #         task_id (Union[str, uuid.UUID, None]): The UUID to assign to the task.
    #             If None, a new UUID will be generated.
    #         case_uuid (str): The UUID of the case.
    #         agent (str): The agent responsible for the task.
    #         module (str): The module associated with the task.
    #         input (str): The input for the task.

    #     Returns:
    #         str: The `task_id` (as a string) of the newly created task.

    #     Raises:
    #         Exception: If the task creation fails.
    #     """
    #     try:
    #         # Generate a new UUID if task_id is not provided
    #         if task_id is None:
    #             logger.error(f"No task_id provided returning...")
    #             return ""

    #         # Insert the new task with the provided or generated task_id
    #         self.cur.execute("""
    #             INSERT INTO osir_tasks (
    #                 task_id,
    #                 case_uuid,
    #                 agent,
    #                 module,
    #                 input,
    #                 processing_status
    #             )
    #             VALUES (%s, %s, %s, %s, %s, 'task_created')
    #         """, (str(task_id), case_uuid, agent, module, input))

    #         # Commit the transaction
    #         self.conn.commit()

    #         logger.debug(f"Task created successfully with task_id: {task_id}")
    #         return str(task_id)

    #     except Exception as e:
    #         # Rollback in case of error
    #         self.conn.rollback()
    #         logger.error(f"Error creating task: {e}")
    #         raise
    
    # def create_handler(
    #     self,
    #     handler_id: Union[str, uuid.UUID, None] = None,
    #     case_uuid: str = None,
    #     modules: list = None,
    #     task_ids: list = None
    # ) -> str:
    #     """
    #     Crée une nouvelle entrée dans la table `osir_handlers` avec un UUID handler_id.

    #     Args:
    #         handler_id (Union[str, uuid.UUID, None]): L'UUID à attribuer au handler.
    #             Si None, une nouvelle UUID sera générée.
    #         case_uuid (str): L'UUID du cas associé.
    #         modules (list): Liste des modules associés au handler.
    #         task_ids (list): Liste des UUIDs des tâches associées.

    #     Returns:
    #         str: L'`handler_id` (sous forme de chaîne) du handler nouvellement créé.

    #     Raises:
    #         Exception: Si la création du handler échoue.
    #     """
    #     try:
    #         # Générer une nouvelle UUID si handler_id n'est pas fourni
    #         if handler_id is None:
    #             logger.error("Aucun handler_id fourni, retour...")
    #             return ""

    #         # Insérer le nouveau handler avec l'ID fourni ou généré
    #         self.cur.execute("""
    #             INSERT INTO osir_handlers (
    #                 handler_id,
    #                 case_uuid,
    #                 modules,
    #                 task_id,
    #                 processing_status
    #             )
    #             VALUES (%s, %s, %s, %s, 'processing_started')
    #         """, (str(handler_id), str(case_uuid), modules, task_ids))

    #         # Valider la transaction
    #         self.conn.commit()

    #         logger.debug(f"Handler créé avec succès avec handler_id: {handler_id}")
    #         return str(handler_id)

    #     except Exception as e:
    #         # Annuler en cas d'erreur
    #         self.conn.rollback()
    #         logger.error(f"Erreur lors de la création du handler: {e}")
    #         raise
    
    # def get_handler_by_id(self, handler_id: str) -> dict:
    #     """
    #     Récupère un handler spécifique depuis la table `osir_handlers` par son UUID.
        
    #     Args:
    #         handler_id (str): L'UUID du handler à rechercher.
            
    #     Returns:
    #         dict: Un dictionnaire contenant les données du handler ou None si non trouvé.
    #     """
    #     try:
    #         self.cur.execute("""
    #             SELECT 
    #                 h.handler_id, h.case_uuid, h.modules, h.processing_status,
    #                 json_agg(json_build_object(
    #                     'task_id', t.task_id,
    #                     'status', t.processing_status,
    #                     'module_name', t.module,
    #                     'created_at', t.timestamp,
    #                     'input', t.input
    #                 )) FILTER (WHERE t.task_id IS NOT NULL) as tasks
    #             FROM osir_handlers h
    #             LEFT JOIN osir_tasks t ON t.task_id = ANY(h.task_id::uuid[])
    #             WHERE h.handler_id = %s::uuid
    #             GROUP BY h.handler_id;
    #         """, (handler_id,))
            
    #         row = self.cur.fetchone()
            
    #         if row:
    #             # On transforme le tuple de la DB en dictionnaire
    #             return {
    #                 "handler_id": str(row[0]),
    #                 "case_uuid": row[1],
    #                 "modules": row[2],  # Sera automatiquement une liste grâce à psycopg2
    #                 "tasks": row[4],  # Liste de UUIDs/Strings
    #                 "processing_status": row[3]
    #             }
            
    #         logger.warning(f"Handler avec l'ID {handler_id} non trouvé.")
    #         return None

    #     except Exception as e:
    #         logger.error(f"Erreur lors de la récupération du handler {handler_id}: {e}")
    #         return None
    
    # def create_osir_handlers_table(self):
    #     """
    #     Crée la table `osir_handlers` dans la base de données PostgreSQL.
    #     La colonne `modules` est de type `TEXT[]` pour stocker une liste de chaînes de caractères.

    #     Structure de la table :
    #     - handler_id (UUID) : Identifiant unique du handler.
    #     - case_uuid (UUID) : Identifiant unique du cas associé.
    #     - modules (TEXT[]) : Liste des modules associés au handler.
    #     - task_id (UUID) : Identifiant unique de la tâche associée.
    #     - processing_status (VARCHAR) : Statut du traitement (par exemple, 'task_created').

    #     Returns:
    #         bool: True si la table a été créée avec succès, False en cas d'erreur.
    #     """
    #     try:
    #         self.cur.execute("""
    #             CREATE TABLE IF NOT EXISTS osir_handlers (
    #                 handler_id UUID PRIMARY KEY,
    #                 case_uuid TEXT NOT NULL,
    #                 modules TEXT[],
    #                 task_id TEXT[],
    #                 processing_status VARCHAR(50) NOT NULL
    #             );
    #         """)

    #         # Commit the transaction
    #         self.conn.commit()
    #         logger.info("Table `osir_handlers` créée avec succès.")
    #         return True

    #     except Exception as e:
    #         # Rollback in case of error
    #         self.conn.rollback()
    #         logger.error(f"Erreur lors de la création de la table `osir_handlers`: {e}")
    #         raise

    # def update_task_status(self, task_id: str, status: ProcessingStatus):
    #     try:
    #         self.cur.execute("""
    #             UPDATE osir_tasks
    #             SET processing_status = %s
    #             WHERE task_id = %s
    #         """, (status.value, task_id))
    #         self.conn.commit()
    #     except Exception as e:
    #         logger.error(f"Error creating table: {e}")
    #         raise

    # def check_input(self, case_uuid: str, input: str) -> bool:
    #     """
    #     Vérifie si une tâche avec le même `input` et `case_uuid` est déjà en statut `processing_started`.

    #     Args:
    #         case_uuid (str): L'UUID du cas.
    #         input (str): L'input de la tâche.

    #     Returns:
    #         bool: True si aucune tâche n'est en cours pour cet input, False sinon.
    #     """
    #     input = str(input)
    #     try:
    #         self.cur.execute("""
    #             SELECT COUNT(*)
    #             FROM osir_tasks
    #             WHERE case_uuid = %s
    #             AND input = %s
    #             AND processing_status = 'processing_started'
    #         """, (case_uuid, input))

    #         count = self.cur.fetchone()[0]
    #         if count > 0:
    #             return True
    #         return False

    #     except Exception as e:
    #         logger.error(f"Erreur lors de la vérification de l'input: {e}")
    #         raise

    # def get_case_handler(self, case_name):
    #     pass

    # def create_table_processing_status(self, table_name):
    #     """
    #     Create a table for processing status if it doesn't exist.

    #     Args:
    #         table_name (str): The name of the table to create.
    #     """
    #     try:
    #         self.cur.execute(f"""
    #             CREATE TABLE IF NOT EXISTS {table_name} (
    #                 id SERIAL PRIMARY KEY,
    #                 case_uuid TEXT,
    #                 case_path TEXT,
    #                 agent TEXT,
    #                 input_file TEXT,
    #                 input_dir TEXT,
    #                 output_file TEXT,
    #                 output_dir TEXT,
    #                 output_prefix TEXT,
    #                 processing_status TEXT,
    #                 timestamp TIMESTAMPTZ DEFAULT NOW()
    #             )
    #         """)
    #         self.conn.commit()
    #     except Exception as e:
    #         logger.error(f"Error creating table: {e}")
    #         raise

    # def _create_table_master_status(self, table_name):
    #     """
    #     Create the master status table if it doesn't exist.

    #     Args:
    #         table_name (str): The name of the table to create.
    #     """
    #     try:
    #         self.cur.execute(f"""
    #             CREATE TABLE IF NOT EXISTS {table_name} (
    #                 id SERIAL PRIMARY KEY,
    #                 case_path TEXT,
    #                 status TEXT,
    #                 case_uuid TEXT,
    #                 modules_selected TEXT,
    #                 timestamp TIMESTAMPTZ DEFAULT NOW()
    #             )
    #         """)
    #         self.conn.commit()
    #     except Exception as e:
    #         logger.error(f"Error creating table: {e}")
    #         raise

    # def store_data(self, case_path, module: OsirModule, status, case_uuid):
    #     """
    #     Store data into the specified module's table.

    #     Args:
    #         case_path (str): The case path.
    #         module (OsirModule): The module instance containing data to store.
    #         status (str): The processing status.
    #         case_uuid (str): The case UUID.
    #     """
    #     # Extracting values from module instance
    #     case_path = str(case_path)
    #     input_file = module.input.match
    #     input_dir = module.input.match
    #     output_file = module.output.output_file
    #     output_dir = module.output.output_dir
    #     output_prefix = module.output.output_prefix
        
    #     # SQL statement with placeholders for each column
    #     self.cur.execute(f"""
    #         INSERT INTO {module.module_name} (
    #             case_uuid, 
    #             case_path,
    #             agent,
    #             input_file, 
    #             input_dir, 
    #             output_file, 
    #             output_dir, 
    #             output_prefix, 
    #             processing_status
    #         )
    #         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    #     """, (
    #         str(case_uuid), 
    #         case_path,
    #         self.host_hostname, 
    #         input_file, 
    #         input_dir, 
    #         output_file, 
    #         output_dir, 
    #         output_prefix, 
    #         status
    #     )
    #     )
    #     self.conn.commit()

    # def update_record(self, module: OsirModule, status, case_uuid):
    #     """
    #     Update an existing record in the specified module's table.

    #     Args:
    #         module (OsirModule): The module instance containing data to update.
    #         status (str): The processing status.
    #         case_uuid (str): The case UUID.
    #     """
    #     try:
    #         # Extracting values from module instance
    #         input_file = module.input.match
    #         input_dir = module.input.match
    #         output_file = module.output.output_file
    #         output_dir = module.output.output_dir
    #         output_prefix = module.output.output_prefix
            
    #         # Create the SET part of the SQL query dynamically
    #         update_data = {
    #             "agent": self.host_hostname,
    #             "input_file": input_file,
    #             "input_dir": input_dir,
    #             "output_file": output_file,
    #             "output_dir": output_dir,
    #             "output_prefix": output_prefix,
    #             "processing_status": status
    #         }
            
    #         set_clause = ', '.join([f"{col} = %s" for col in update_data.keys()])
    #         values = list(update_data.values())

    #         # Add values for the WHERE clause
    #         values.append(case_uuid)

    #         # Define the SQL UPDATE query
            
    #         update_query = f"""
    #         UPDATE {module.module_name}
    #         SET {set_clause}
    #         WHERE case_uuid = %s
    #             AND ((input_file != '' AND input_file = %s)
    #             OR (input_dir != '' AND input_dir = %s))
    #         """

    #         # Execute the SQL query with the correct values order
    #         self.cur.execute(update_query, values + [input_file, input_dir])

    #         # Commit the changes
    #         self.conn.commit()

    #         # Check if the record was updated
    #         rows_updated = self.cur.rowcount
    #         logger.debug(f"Database updates {rows_updated} record(s).")

    #     except Exception as error:
    #         logger.error(f"Error updating record: {error}")
        
    # def store_master_status(self, case_path, status, case_uuid, modules_selected):
    #     """
    #     Store or update the master status for a given case.

    #     Args:
    #         case_path (str): The case path.
    #         status (str): The processing status.
    #         case_uuid (str): The case UUID.
    #         modules_selected (str): The selected modules.
    #     """
    #     case_path = str(case_path)
    #     current_timestamp = datetime.datetime.now()
    #     try:
    #         # Check if the record exists
    #         self.cur.execute("""
    #             SELECT 1 FROM master_status WHERE case_path = %s
    #         """, (case_path,))
    #         exists = self.cur.fetchone()

    #         if exists:
    #             # Record exists, update it
    #             self.cur.execute("""
    #                 UPDATE master_status
    #                 SET status = %s, case_uuid = %s, timestamp = %s, modules_selected = %s
    #                 WHERE case_path = %s
    #             """, (status, case_uuid, current_timestamp, modules_selected, case_path))
    #         else:
    #             # Record does not exist, insert new one
    #             self.cur.execute("""
    #                 INSERT INTO master_status (case_path, status, case_uuid, modules_selected)
    #                 VALUES (%s, %s, %s, %s)
    #             """, (case_path, status, case_uuid, modules_selected))

    #         # Commit the changes
    #         self.conn.commit()

    #         # Log the result
    #         action = "Updated" if exists else "Inserted"
    #         logger.debug(f"{action} master_status record for case_path: {case_path}")

    #     except Exception as error:
    #         logger.error(f"Error in add_or_update_master_status: {error}")
    #         self.conn.rollback()
            
    # def close(self):
    #     """
    #     Close the database connection.
    #     """
    #     self.cur.close()
    #     self.conn.close()
        
    # def check_input_file(self, case_uuid, input_file):
    #     try:
    #         """
    #         Checks if the specified input file is currently being processed in any table except 'master_status' and 'case_snapshot'.

    #         Args:
    #             case_uuid (str): The UUID of the case.
    #             input_file (str): The path of the input file to check.

    #         Returns:
    #             bool: True if the input file is currently being processed, False otherwise.
    #         """
    #         # Query to check if the input_file exists with processing_status not as "processing_done"
    #         query = sql.SQL("""
    #             SELECT table_name
    #             FROM information_schema.tables
    #             WHERE table_schema='public' AND table_name != 'master_status' AND table_name != 'case_snapshot'
    #         """)
    #         self.cur.execute(query)
    #         tables = self.cur.fetchall()

    #         for table in tables:
    #             query = sql.SQL("""
    #                 SELECT 1
    #                 FROM {}
    #                 WHERE case_uuid = %s AND input_file = %s AND processing_status = 'processing_started'
    #                 LIMIT 1
    #             """).format(sql.Identifier(table[0]))
    #             self.cur.execute(query, (case_uuid, input_file))
    #             if self.cur.fetchone():
    #                 logger.debug(f"Query: {self.cur.mogrify(query, (case_uuid, input_file))}")
    #                 return True
            
    #         return False

    #     except Exception as e:
    #         logger.error(f"Error: {str(e)}")
    #         return False
        
    # def check_input_dir(self, case_uuid, input_dir):
    #     """
    #     Checks if the specified input directory or its sub-items are currently being processed in any table except 'master_status'.
    #     Following table are excluded : 'processing_done', 'case_snapshot'
    #     Args:
    #         case_uuid (str): The UUID of the case.
    #         input_dir (str): The path of the input directory to check.

    #     Returns:
    #         bool: True if the input directory or its sub-items are currently being processed, False otherwise.
    #     """
    #     try:
    #         # Query to check if the input_dir exists or is a sub item with processing_status not as "processing_done"
    #         query = sql.SQL("""
    #             SELECT table_name
    #             FROM information_schema.tables
    #             WHERE table_schema='public' AND table_name != 'master_status' AND table_name != 'case_snapshot'
    #         """)
    #         self.cur.execute(query)
    #         tables = self.cur.fetchall()

    #         for table in tables:
    #             query = sql.SQL("""
    #                 SELECT 1
    #                 FROM {}
    #                 WHERE case_uuid = %s AND (
    #                     input_dir = %s OR input_dir LIKE %s OR input_file LIKE %s
    #                 ) AND processing_status = 'processing_started'
    #                 LIMIT 1
    #             """).format(sql.Identifier(table[0]))
    #             self.cur.execute(query, (case_uuid, input_dir, f'{input_dir}%', f'{input_dir}%'))
    #             if self.cur.fetchone():
    #                 return True
            
    #         return False

    #     except Exception as e:
    #         print(f"Error: {e}")
    #         return False
        
    # def is_processing_active(self, case_uuid):
    #     """
    #     Check if there is at least one table with a row for the given case_uuid
    #     that has a column processing_status not equal to 'processing_done'.
    #     Following table are excluded : 'processing_done', 'case_snapshot'

    #     Args:
    #         case_uuid (str): The case UUID.

    #     Returns:
    #         bool: True if such a row exists, False otherwise.
    #     """
    #     """
    #     Vérifie si une tâche avec le même `input` et `case_uuid` est déjà en statut `processing_started`.

    #     Args:
    #         case_uuid (str): L'UUID du cas.
    #         input (str): L'input de la tâche.

    #     Returns:
    #         bool: True si aucune tâche n'est en cours pour cet input, False sinon.
    #     """
    #     try:
    #         self.cur.execute("""
    #             SELECT COUNT(*)
    #             FROM osir_tasks
    #             WHERE case_uuid = %s
    #             AND processing_status = 'processing_started'
    #         """, (str(case_uuid),))

    #         count = self.cur.fetchone()[0]
    #         if count > 0:
    #             return True
    #         return False

    #     except Exception as e:
    #         logger.error(f"Erreur lors de la vérification de l'input: {e}")
    #         raise
            
    # def _create_case_snapshot_table(self):
    #     """
    #     Ensure the `case_snapshot` table exists in the database.
    #     """
    #     query = """
    #     CREATE TABLE IF NOT EXISTS case_snapshot (
    #         case_uuid TEXT NOT NULL,
    #         case_path TEXT NOT NULL,
    #         path TEXT NOT NULL,
    #         entry_type TEXT NOT NULL,
    #         PRIMARY KEY (case_uuid, path)
    #     )
    #     """
    #     try:
    #         self.cur.execute(query)
    #         self.conn.commit()
    #         logger.debug("Table `case_snapshot` ensured.")
    #     except Exception as e:
    #         logger.error(f"Error creating `case_snapshot` table: {str(e)}")
    #         self.conn.rollback()

    # def get_stored_case_snapshot(self, case_path):
    #     """
    #     Retrieve stored directory entries for the specified case UUID.

    #     Args:
    #         case_path (str): The path of the case.

    #     Returns:
    #         list: A list of (path, entry_type) tuples.
    #     """
    #     case_path = str(case_path)
    #     query = """
    #     SELECT path, entry_type
    #     FROM case_snapshot
    #     WHERE case_path = %s
    #     """
    #     try:
    #         self.cur.execute(query, (case_path,))
    #         rows = self.cur.fetchall()
    #         logger.debug(f"Retrieved {len(rows)} entries for case_path: {case_path}")
    #         return [(row[0], row[1]) for row in rows]
    #     except Exception as e:
    #         logger.error(f"Error fetching entries for case_path {case_path}: {str(e)}")
    #         return []

    # def store_case_snapshot(self, case_uuid, case_path, entries_list):
    #     import io
    #     try:
    #         case_path = str(case_path)
    #         # 1) Delete old entries first
    #         delete_query = "DELETE FROM case_snapshot WHERE case_uuid = %s"
    #         self.cur.execute(delete_query, (case_uuid,))
    #         # 2) Prepare data as CSV format in memory
    #         output = io.StringIO()
    #         for path, entry_type in entries_list:
    #             path=str(path)
    #             if '\\' in path:
    #                 logger.warning(f"Skipping entry due to invalid backslash: path={path}, entry_type={entry_type}")
    #                 continue
    #             output.write(f"{case_uuid}\t{case_path}\t{path}\t{entry_type}\n")
    #         output.seek(0)  # Move cursor back to start

    #         # 3) Use copy_from to bulk-insert
    #         self.cur.copy_from(
    #             file=output,
    #             table='case_snapshot',
    #             columns=('case_uuid', 'case_path', 'path', 'entry_type'),
    #             null=''  # specify how to handle NULL if needed
    #         )

    #         # 4) Commit changes
    #         self.conn.commit()
    #     except Exception as e:
    #         self.conn.rollback()
    #         logger.error(f"Bulk insert error for case_uuid {case_uuid}: {str(e)}")


OSIR_DB = DbOSIR()
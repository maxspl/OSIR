import streamlit as st
import pandas as pd
import requests
from sqlalchemy import text
from utils.Db import Db_accessor
from datetime import datetime, timedelta
import pytz  # You might need to install pytz if not already available
from streamlit_extras.colored_header import colored_header 
from src.web_app.utils import MasterSideBar


# Database formatter class
class MasterStatus:
    def __init__(self):
        """
        Initialize the MasterStatus class, setting up the database accessor.
        """
        self.db_accessor = Db_accessor()

    def display_tables(self):
        """
        Retrieve and display the master status table with added comments and colors.

        Returns:
            None
        """
        query = text("SELECT * FROM master_status")
        try:
            df = pd.read_sql(query, con=self.db_accessor.engine)
            df = self.add_comments_and_colors(df)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.warning(f"DB access error: {str(e)}")
            st.info("This may be normal if no data has been processed yet.")

    def add_comments_and_colors(self, df):
        """
        Add comments and color styling to the dataframe based on the processing status and timestamp.

        Args:
            df (pd.DataFrame): The dataframe to be styled.

        Returns:
            pd.Styler: The styled dataframe.
        """
        # Ensure 'timestamp' is in datetime format and aware
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        
        # Convert modules_selected to a list
        df['modules_selected'] = df['modules_selected'].apply(lambda x: x.strip('{}').split(','))

        current_time = datetime.now(pytz.utc)
        four_hours_ago = current_time - timedelta(hours=4)

        def style_row(row):
            if 'processing_case' in row['status'] and row['timestamp'] < four_hours_ago:
                return ['background-color: lightcoral; color: lightgrey;'] * len(row)
            elif 'processing_done' in row['status']:
                return ['background-color: lightgreen; color: gray;'] * len(row)
            elif 'processing_case' in row['status']:
                return ['background-color: orange; color: gray;'] * len(row)
            else:
                return [''] * len(row)

        styled_df = df.style.apply(style_row, axis=1)
        return styled_df

    def get_flower_workers(self, flower_api_url):
        """
        Retrieve worker information from the Flower API.

        Args:
            flower_api_url (str): The URL of the Flower API.

        Returns:
            dict or None: A dictionary containing worker information if successful, None otherwise.
        """
        response = requests.get(f"{flower_api_url}/api/workers?status=True")
        if response.status_code == 200:
            workers = response.json()
            return workers
        else:
            return None

    def display_flower_workers(self, flower_api_url):
        """
        Retrieve and display worker information from the Flower API with color styling.

        Args:
            flower_api_url (str): The URL of the Flower API.

        Returns:
            None
        """
        def style_row(row):
            if 'Offline' in row['Status']:
                return ['background-color:  lightcoral; color: lightgray;'] * len(row)
            elif 'Online' in row['Status']:
                return ['background-color: lightgreen; color: gray;'] * len(row)
            
        workers = self.get_flower_workers(flower_api_url)
        if workers:
            worker_data = []
            for worker, worker_status in workers.items():
                
                worker_data.append({
                    'Agent host': worker.split("@")[1],
                    'Worker': worker.split("@")[0],
                    'Status': 'Online' if worker_status else 'Offline'
                })
            df_workers = pd.DataFrame(worker_data)
            styled_df = df_workers.style.apply(style_row, axis=1)
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.warning("Failed to retrieve worker information from Flower.")
            st.info("This may be normal if no data has been processed yet.")

    # def display_flower_tasks(self, flower_api_url):
    """
    Unused for the moment, I cant find a solution to avoid truncated args.
    """
    #     # Append the tasks endpoint to the flower API URL
    #     flower_api_url += "/api/tasks"

    #     # Make a GET request to the Flower API
    #     response = requests.get(flower_api_url)
        
    #     # Check if the response is successful
    #     if response.status_code == 200:
    #         tasks = response.json()
    #     else:
    #         print(f"Failed to retrieve tasks, status code: {response.status_code}")
    #         return None

    #     # Prepare task data for DataFrame
    #     task_list = []
    #     for task_id, task_info in tasks.items():
    #         # Extract args
    #         args = task_info.get('args', [])
    #         st.error("msp ici")
    #         if args and len(args) == 3:
    #             case_path, module_bytes, case_uuid = args
    #             # try:
    #             #     module_instance = pickle.loads(module_bytes)
    #             # except (pickle.UnpicklingError, TypeError) as e:
    #             #     module_instance = f"Error deserializing: {e}"
    #         else:
    #             case_path, module_instance, case_uuid = 'N/A', 'N/A', 'N/A'
    #         import json
    #         #$test = json.loads(args.replace('(', '[').replace(')', ']').replace("'", '"'))
    #         st.error(f"msp ici {len(args)}")
    #         print(args)
    #         task_details = {
    #             'task_id': task_id,
    #             'name': task_info.get('name', 'N/A'),
    #             'args': task_info.get('args', 'N/A'),
    #             'kwargs': task_info.get('kwargs', 'N/A'),
    #             'state': task_info.get('state', 'N/A'),
    #             'received': task_info.get('received', 'N/A'),
    #             'started': task_info.get('started', 'N/A'),
    #             'succeeded': task_info.get('succeeded', 'N/A'),
    #             'failed': task_info.get('failed', 'N/A'),
    #             'retried': task_info.get('retried', 'N/A'),
    #             'case_path_msp': case_path
    #         }
    #         task_list.append(task_details)

    #     # Create a DataFrame
    #     df = pd.DataFrame(task_list)
        
    #     st.dataframe(df, use_container_width=True)


st.set_page_config(
    page_title="OSIR",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://<change-me>",
        "Report a bug": "https://<change-me>",
        "About": "OSIR"
    }
)
master_status = MasterStatus()

tab1, tab2, tab3 = st.tabs(["Master Status", "Running Workers", "Tasks details"])

with tab1:
    colored_header(
        label="Master - Processor Status",
        description="",
        color_name="violet-70",
    )
    master_status.display_tables()

with tab2:
    colored_header(
        label="Running Workers",
        description="",
        color_name="violet-70",
    )

    flower_api_url = "http://flower:5555" 
    master_status.display_flower_workers(flower_api_url)
    

with tab3:
    master_sidebar = MasterSideBar.SystemManager(key="masteragentstatus")
    location_details = master_sidebar.location_details
    host = location_details["hostname"]

    # Set the URL for the iframe
    iframe_url = f"http://{host}:5555/"

    # Use the HTML component to embed the iframe
    st.markdown(f"""
        <iframe src="{iframe_url}" width="100%" height="600"></iframe>
    """, unsafe_allow_html=True)

# Sidebar
MasterSideBar.sidebar()
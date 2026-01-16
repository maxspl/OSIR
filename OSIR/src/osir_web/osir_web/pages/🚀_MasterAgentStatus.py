import streamlit as st
import pandas as pd
import requests
from sqlalchemy import text
import pytz
from streamlit_extras.colored_header import colored_header

from osir_web.utils import MasterSideBar

# Database formatter class


class MasterStatus:
    def __init__(self):
        """
        Initialize the MasterStatus class
        """

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
            st.dataframe(styled_df, width='stretch')
        else:
            st.warning("Failed to retrieve worker information from Flower.")
            st.info("This may be normal if no data has been processed yet.")


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

tab2, tab3 = st.tabs(["Running Workers", "Tasks details"])

with tab2:
    colored_header(
        label="Running Workers",
        description="",
        color_name="violet-70",
    )

    flower_api_url = "http://master-flower:5555"
    master_status.display_flower_workers(flower_api_url)


with tab3:
    master_sidebar = MasterSideBar.SystemManager(key="masteragentstatus")
    location_details = master_sidebar.location_details
    if location_details and "hostname" in location_details:
        host = location_details["hostname"]
    else:
        host = "localhost"

    # Set the URL for the iframe
    iframe_url = f"http://{host}:5555/"

    # Use the HTML component to embed the iframe
    st.markdown(f"""
        <iframe src="{iframe_url}" width="100%" height="600"></iframe>
    """, unsafe_allow_html=True)

# Sidebar
MasterSideBar.sidebar()

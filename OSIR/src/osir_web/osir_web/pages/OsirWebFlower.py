import requests

import streamlit as st
import pandas as pd

from streamlit_extras.colored_header import colored_header

from osir_lib.core.OsirAgentConfig import OsirAgentConfig
from osir_web.pages.OsirWebHeader import OsirWebHeader
from osir_web.pages.OsirWebUtils import OsirWebUtils

class OsirWebFlower:
    @staticmethod
    def render():
        OsirWebHeader.render(
            title="Master & Agent Status",
            subtitle="Monitor your agent & master using Flower",
        )
        OsirWebUtils.center_tabs()
        tab1, tab2 = st.tabs(["Running Workers", "Tasks details"])

        OsirWebFlower.tab1_running_workers(tab1)
        OsirWebFlower.tab2_tasks_details(tab2)

    @staticmethod
    def tab1_running_workers(tab):
        def style_row(row):
            if 'Offline' in row['Status']:
                return ['background-color:  lightcoral; color: lightgray;'] * len(row)
            elif 'Online' in row['Status']:
                return ['background-color: lightgreen; color: gray;'] * len(row)
                
        with tab:
            flower_api_url = "http://master-flower:5555"
            
            response = requests.get(f"{flower_api_url}/api/workers?status=True")
            if response.status_code == 200:
                workers = response.json()
            else:
                workers = None

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


    @staticmethod
    def tab2_tasks_details(tab):
        with tab:
            try:
                master_host = OsirAgentConfig().master_host
            except FileNotFoundError:
                master_host = "localhost"

            iframe_url = f"http://{master_host}:5555/"

            # Use the HTML component to embed the iframe
            st.markdown(f"""
                <iframe src="{iframe_url}" width="100%" height="600"></iframe>
            """, unsafe_allow_html=True)
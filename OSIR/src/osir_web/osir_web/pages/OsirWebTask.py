import pandas as pd
import streamlit as st

from osir_web.pages.OsirWebUtils import OsirWebUtils
from osir_web.pages.OsirWebHeader import OsirWebHeader

from osir_service.postgres.OsirDb import OsirDb

from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()

class OsirWebTask:

    @staticmethod
    def _init_session_state():
        """Initialize session state variables if they don't exist."""
        if "switch_count" not in st.session_state:
            st.session_state.switch_count = 0
        if "selected_task_id" not in st.session_state:
            st.session_state.selected_task_id = ""
        if "selected_handler_id" not in st.session_state:
            st.session_state.selected_handler_id = ""
        if "selected_case_name" not in st.session_state:
            st.session_state.selected_case_name = ""

    @staticmethod
    def render():
        OsirWebHeader.render(
            title="Status - Task On-Going",
            subtitle="Find and monitor your on going tasks",
        )
        OsirWebUtils.center_tabs()

        tab1 = st.tabs(["Tasks On-Going"])
        OsirWebTask.tab1_task_ongoing(tab1[0])

    def tab1_task_ongoing(tab):
        with tab:
            filters = OsirWebUtils.filters(
                show_case_name=True
            )
            st.echo("df")
            with OsirDb() as db:
                tasks = db.task.list(processing_status=["task_created", "processing_started"])
            if tasks:
                tasks = [task.model_dump(mode='json') for task in tasks]
                df = pd.DataFrame(tasks)
                uuid_columns = ["case_uuid", "task_id"]
                for col in uuid_columns:
                    if col in df.columns:
                        df[col] = df[col].astype(str)

                if 'agent' in df.columns:
                    df.drop(columns=['agent'], inplace=True)
                
                styled_df = df.style.apply(OsirWebUtils.color_rows, axis=1)
                st.dataframe(styled_df, width='stretch')
            else:
                st.info("No task Found")
    
    

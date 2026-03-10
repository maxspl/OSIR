import pandas as pd
from osir_web.pages.OsirWebFile import OsirWebFile
import streamlit as st

from osir_web.pages.OsirWebUtils import OsirWebUtils
from osir_web.pages.OsirWebHeader import OsirWebHeader
from osir_web.pages.OsirWebMonitoring import OsirWebMonitoring
from osir_service.postgres.OsirDb import OsirDb

from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()


class OsirWebTask:

    @staticmethod
    def _init_session_state():
        """Initialize session state variables if they don't exist."""
        if "selected_task_id" not in st.session_state:
            st.session_state.selected_task_id = ""
        if "monitoring_task_switch" not in st.session_state:
            st.session_state.monitoring_task_switch = False

    @staticmethod
    def render():
        OsirWebHeader.render(
            title="Status - Task On-Going",
            subtitle="Find and monitor your on going tasks",
        )
        OsirWebTask._init_session_state()
        OsirWebUtils.center_tabs()

        tab1 = st.tabs(["Tasks On-Going"])
        OsirWebTask.tab1_task_ongoing(tab1[0])

    def tab1_task_ongoing(tab):
        with tab:
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

                event = st.dataframe(
                    styled_df, 
                    on_select="rerun",
                    selection_mode="single-cell",  # Allows clicking a line
                    width='stretch')

                # Check if a cell was clicked
                if event.selection.cells:
                    selected_cell = event.selection.cells[0]
                    selected_row_index = selected_cell[0]

                    selected_row = df.iloc[selected_row_index]

                    previous_selected_task = st.session_state.selected_task_id
                    st.session_state.selected_task_id = selected_row["task_id"]

                    if previous_selected_task != selected_row["task_id"]:
                        st.session_state.monitoring_task_switch = True
                        st.switch_page(
                            st.Page(OsirWebMonitoring.render, title="Orchestration Monitoring", url_path='OsirWebMonitoring')
                        ) 
            else:
                st.info("No task Found")
    
    

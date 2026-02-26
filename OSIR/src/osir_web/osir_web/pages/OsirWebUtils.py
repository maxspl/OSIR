import time
from typing import Optional
import uuid

from pydantic import BaseModel
import streamlit as st

from streamlit.components.v1 import html
from osir_service.postgres.OsirDb import OsirDb
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()

class OsirWebFilters(BaseModel):
    case_name: Optional[str] = None
    input: Optional[str] = None
    task_id: Optional[str] = None
    output: Optional[str] = None
    processing_status: Optional[str] = None
    handler_id: Optional[str] = None
    module: Optional[str] = None

class OsirWebUtils:

    @staticmethod
    def center_tabs(switch: bool = True):
        st.markdown("""
        <style>
            .stTabs [data-baseweb="tab-list"] {
                justify-content: center;
            }
        </style>
        """, unsafe_allow_html=True)
        if switch:
            OsirWebUtils.switch(0)

    @staticmethod
    def switch(tab_index):
        switch_html = f"""
            <script>
            // Unique ID: {time.time()} 
            setTimeout(function() {{
                var tabButtons = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
                if (tabButtons.length > {tab_index}) {{
                    tabButtons[{tab_index}].click();
                }}
            }}, 100);
            </script>
        """
        html(switch_html, height=0, width=0)

    
    @staticmethod
    def color_rows(row):
        if row["processing_status"] == "processing_done":
            return ["background-color: lightgreen; color: gray;"] * len(row)
        elif row["processing_status"] == "processing_failed":
            return ["background-color:  lightcoral;"] * len(row)
        elif row["processing_status"] == "processing_started":
            return ["background-color:  orange;"] * len(row)
        elif row["processing_status"] == "task_created":
            return ["background-color: lightblue; color: gray;"] * len(row)
        else:
            return [""] * len(row)
    
    @staticmethod
    def filters(
        show_case_name: bool = False,
        show_input: bool = False,
        show_handler_id: bool = False,
        show_output: bool = False,
        show_processing_status: bool = False,
        show_module: bool = False,
        case_name: Optional[str] = None,
        input_: Optional[str] = None,
        output: Optional[str] = None,
        processing_status: Optional[str] = None,
        handler_id: Optional[list[str]] = None,
        modules: Optional[list[str]] = None,
        key: Optional[str] = uuid.uuid4()
    ):
        with st.expander("🔍 Filters", expanded=False):
            # Create a list of columns (2 columns per row)
            columns = st.columns(2)
            col_index = 0  # Track the current column index

            # Helper function to get the next available column
            def next_col():
                nonlocal col_index
                col = columns[col_index % 2]  # Alternate between 0 and 1
                col_index += 1
                return col

            # Render filters dynamically
            if show_case_name:
                with next_col():
                    all_case = []
                    with OsirDb() as db:
                        cases = db.case.list()
                        if cases:   
                            all_case = [x.name for x in cases]
                            
                    case_options = list([""] + all_case)
                    if case_name:
                        try:
                            case_index = case_options.index(case_name)
                        except ValueError:
                            case_index = 0
                    else:
                        case_index = 0

                    filter_case = st.selectbox(
                        "Case name",
                        case_options,
                        placeholder=f"{key} e.g. case_001",
                        index=int(case_index)
                    )
            else:
                filter_case = case_name

            if show_input:
                with next_col():
                    filter_input = st.text_input(
                        "Input",
                        value=input_ or "",
                        placeholder="e.g. /mnt/evidence",
                        key=f"filter_input_for_{key}"
                    )
            else:
                filter_input = input_

            if show_output:
                with next_col():
                    filter_output = st.text_input(
                        "Output",
                        value=output or "",
                        placeholder="e.g. /mnt/evidence",
                        key=f"filter_output_for_{key}"
                    )
            else:
                filter_output = output

            if show_processing_status:
                with next_col():
                    filter_processing_status = st.selectbox(
                        "Filter by Processing Status :",
                        options=["", "task_created", "processing_started", "processing_done", "processing_failed"],
                        key=f"filter_processing_status_for_{key}"
                    )
            else:
                filter_processing_status = processing_status

            if show_handler_id:
                with next_col():
                    with OsirDb() as db:
                        handler_ids = [""]
                        handler_index = 0
                        if filter_case:
                            case_uuid = db.case.get(name=filter_case).case_uuid
                            handlers = db.handler.list(case_uuid=case_uuid)
                            if handlers:
                                handler_ids = [""] + [str(handler.handler_id) for handler in handlers]
                                if handler_id:
                                    try:
                                        handler_index = handler_ids.index(handler_id)
                                    except: 
                                        handler_index=0                                    

                    filter_show_handler_id = st.selectbox(
                        "Filter by Handler ID :",
                        options=handler_ids,
                        placeholder=f"{key}",
                        index=handler_index
                    )
            else:
                filter_show_handler_id = handler_id

            if show_module:
                with next_col():
                    modules = []
                    if filter_case:
                        with OsirDb() as db:
                            case_uuid = db.case.get(name=filter_case).case_uuid
                            task_list = db.task.list(case_uuid=case_uuid)
                    else:
                        task_list = []

                    modules = list(set([str(t.module) for t in task_list]))
                    
                    filter_module = st.selectbox(
                        "Filter by Module :",
                        options=[""] + modules,
                        placeholder=f"{key}"
                    )
            else:
                filter_module = modules

        return OsirWebFilters(
            case_name=filter_case,
            input=filter_input,
            output=filter_output,
            processing_status=filter_processing_status,
            handler_id=filter_show_handler_id,
            module=filter_module
        )
    
    @staticmethod
    def delete_handler_task(case_name):
        if case_name:
            with OsirDb() as db:
                case_uuid = db.case.get(name=case_name).case_uuid
                db.handler.delete(case_uuid=case_uuid)
                db.task.delete(case_uuid=case_uuid)
                st.rerun()

    def toast(txt: str = "Task started!", icon: str = "🎉", background: Optional[str] = "#28a745"):
        st.markdown(f"""
            <style>
            /* Toast container position */
            div[data-testid="stToastContainer"] {{
                bottom: 1rem;
                right: 1rem;
                top: auto;
                left: auto;
            }}

            /* Toast background color */
            div[data-testid="stToast"] {{
                background-color: {background} !important;
                color: white !important;
            }}
            </style>
        """, unsafe_allow_html=True)

        st.toast(txt, icon=icon)
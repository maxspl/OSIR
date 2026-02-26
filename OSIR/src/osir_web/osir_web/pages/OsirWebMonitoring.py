import pandas as pd
import streamlit as st
from osir_web.pages.OsirWebCase import FileManager
from osir_web.pages.OsirWebHeader import OsirWebHeader
from osir_web.pages.OsirWebUtils import OsirWebUtils
from osir_service.postgres.OsirDb import OsirDb
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()

class OsirWebMonitoring:
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
        if "center_tabs_monitoring" not in st.session_state:
            st.session_state.center_tabs_monitoring = True

    @staticmethod
    def render():
        OsirWebHeader.render(
            title="Orchestration Monitoring",
            subtitle="Find and monitor your on going handlers",
        )
        OsirWebMonitoring._init_session_state()

        if st.session_state["center_tabs_monitoring"]:
            OsirWebUtils.center_tabs(switch=True)
            st.session_state.center_tabs_monitoring = False
        else:
            OsirWebUtils.center_tabs(switch=False)

        tab1, tab2, tab3 = st.tabs(["Handler By Case", "Task by Case", "Task Logs"])

        OsirWebMonitoring.tab1_handler_by_case(tab1)
        OsirWebMonitoring.tab2_tasks_by_case(tab2)
        OsirWebMonitoring.tab3_task_log(tab3)

    @staticmethod
    def tab1_handler_by_case(tab):
        with tab:
            all_cases = FileManager.all_cases()

            filters = OsirWebUtils.filters(
                show_case_name=True,
                show_processing_status=True,
                key="tab1"
            )

            with OsirDb() as db:
                case = None
                if filters.case_name:
                    case = db.case.create(name=filters.case_name)

                handlers = db.handler.list(
                    case_uuid=case.case_uuid if case else None,
                    processing_status=filters.processing_status if filters.processing_status else None
                )
            js_trigger = st.empty()

            if handlers:
                df = pd.DataFrame([x.model_dump(mode='json') for x in handlers])
                uuid_columns = ["handler_id", "case_uuid", "created_at"]
                for col in uuid_columns:
                    if col in df.columns:
                        df[col] = df[col].astype(str)

                df["created_at"] = df["created_at"].str[:19]
                
                if "task_ids" in df.columns:
                    df["task_ids"] = df["task_ids"].apply(
                        lambda task_list: [str(task) for task in task_list] if isinstance(task_list, list) else str(task_list)
                    )

                columns_order = ["created_at", "case_name", "modules", "processing_status"]
                other_columns = [col for col in df.columns if col not in columns_order]
                columns_order.extend(other_columns)

                df = df[columns_order]

                df.drop(columns=['case_uuid'], inplace=True)

                sorted_df = df.sort_values(by="created_at", ascending=False)
                styled_df = sorted_df.style.apply(OsirWebUtils.color_rows, axis=1)

                event = st.dataframe(
                    styled_df,
                    on_select="rerun",
                    selection_mode="single-cell",  # Allows clicking a line
                    hide_index=True,
                    width='stretch',
                    height=600,
                    column_config={
                        "created_at": st.column_config.DatetimeColumn(
                            "Created At",
                            format="YYYY-MM-DD HH:mm:ss"  
                        ),
                         "case_name": st.column_config.TextColumn(
                            "Case Name"  
                        ),
                        "modules": st.column_config.ListColumn(
                            "Modules"  
                        ),
                        "processing_status": st.column_config.TextColumn(
                            "Processing Status"  
                        ),
                        "task_id": st.column_config.ListColumn(
                            "Task IDs"  
                        ),
                        "handler_id": st.column_config.TextColumn(
                            "Handler ID"  
                        )
                    }
                )

                # Check if a cell was clicked
                if event.selection.cells:
                    # event.selection.cells[0] is a tuple: (row_index, col_index)
                    selected_cell = event.selection.cells[0]
                    selected_row_index = selected_cell[0]  # Access the row (first part of tuple)

                    # Retrieve data from the original DataFrame using .iloc
                    selected_row = sorted_df.iloc[selected_row_index]

                    previous_handler_id = st.session_state.selected_handler_id

                    # Save values to session state for Tab 2
                    logger.info(selected_row["case_name"])
                    st.session_state.selected_case_name = str(selected_row["case_name"])
                    st.session_state.selected_handler_id = str(selected_row["handler_id"])
                    event = pd.DataFrame()
                    # Trigger the JS switch by writing to the placeholder
                    if previous_handler_id != selected_row["handler_id"]:
                        with js_trigger:
                            OsirWebUtils.switch(1)


            else:
                st.info("No handler found.")

            if filters.case_name:
                with st.expander("⚠️ Dangerous action: Clear all tables for this case"):
                    st.warning("This will permanently delete all entries in all database tables related to the selected case.")
                    confirm_delete = st.checkbox("I understand the consequences and want to proceed with deletion.", key="all")

                    if st.button("❌ Clear all tables for this case", type="primary", disabled=not confirm_delete):
                        with st.spinner(f"Deleting entries for case: {filters.case_name}..."):
                            OsirWebUtils.delete_handler_task(filters.case_name)
                        st.success(f"✅ All data related to case '{filters.case_name}' was deleted from the database.")
    
    @staticmethod
    def tab2_tasks_by_case(tab):
        with tab:
            passed_case_name = st.session_state.get('selected_case_name', "")
            passed_handler_id = st.session_state.get('selected_handler_id', "")

            filters = OsirWebUtils.filters(
                show_case_name=True,
                show_processing_status=True,
                show_handler_id=True,
                show_module=True,
                case_name=passed_case_name,
                handler_id=passed_handler_id,
                key="tab2"
            )

            # --- Display Results ---
            OsirWebMonitoring.tab2_tasks_by_case_table(
                selected_case_name=filters.case_name,
                selected_task_status=filters.processing_status,
                selected_handler_id=filters.handler_id,
                selected_module=filters.module
            )

            if filters.handler_id:
                with st.expander("⚠️ Dangerous action: Delete this Handler"):
                    st.warning(f"This will permanently delete handler '{filters.handler_id}' and all its associated tasks.")
                    confirm_delete = st.checkbox("I understand the consequences and want to proceed with deletion.", key="handler")

                    if st.button("❌ Delete Handler and Associated Tasks", type="primary", disabled=not confirm_delete):
                        with st.spinner(f"Deleting : {filters.handler_id}..."):
                            with OsirDb() as db:
                                db.task.delete(handler_id=filters.handler_id)
                                db.handler.delete(handler_id=filters.handler_id)
                            filters.handler_id = ""
                            st.session_state.selected_handler_id = ""
                            st.rerun()
                        st.success(f"✅ All data related to '{filters.handler_id}' was deleted from the database.")
    
    @staticmethod
    def tab2_tasks_by_case_table(selected_case_name, selected_task_status=None, selected_handler_id=None, selected_module=None):
        if selected_case_name:
            with OsirDb() as db:
                case_uuid = db.case.get(name=selected_case_name).case_uuid
                tasks_by_case = db.task.list(
                    case_uuid=case_uuid,
                    processing_status=selected_task_status if selected_task_status else None
                )
                js_trigger = st.empty()
                if tasks_by_case:
                    df = pd.DataFrame([x.model_dump(mode='json') for x in tasks_by_case])

                    for col in df.columns:
                        if df[col].dtype == 'object':
                            df[col] = df[col].apply(lambda x: str(x) if x is not None else "")

                    if selected_handler_id:
                        handler_info = db.handler.get(handler_id=selected_handler_id)

                        if handler_info:
                            if handler_info.task_id:
                                target_task_ids = [str(tid) for tid in handler_info.task_id]
                            else:
                                target_task_ids = []
                            if "task_id" in df.columns:
                                df = df[df["task_id"].isin(target_task_ids)]
                        else:
                            df = pd.DataFrame()

                    if selected_module and not df.empty and "module" in df.columns:
                        df = df[df["module"].apply(lambda x: selected_module in x if isinstance(x, list) else x == selected_module)]

                    if not df.empty:
                        if 'agent' in df.columns:
                            df.drop(columns=['agent'], inplace=True)

                        styled_df = df.style.apply(OsirWebUtils.color_rows, axis=1)

                        event = st.dataframe(
                            styled_df,
                            on_select="rerun",
                            selection_mode="single-cell",
                            hide_index=True,
                            width='stretch',
                            height=600
                        )

                        if event.selection.cells:
                            selected_cell = event.selection.cells[0]
                            selected_row_index = selected_cell[0] 

                            selected_row = df.iloc[selected_row_index]

                            previous_task_id = st.session_state.selected_task_id
                            st.session_state.selected_task_id = str(selected_row["task_id"])
                            if previous_task_id != selected_row["task_id"]:
                                with js_trigger:
                                    OsirWebUtils.switch(2)

                    else:
                        st.info("No tasks match the selected criteria.")
                else:
                    st.info("No tasks found for this case.")
        else:
            st.info("Please select a case name.")

    @staticmethod
    def tab3_task_log(tab):
        with tab:
            passed_task_id = st.session_state.get('selected_task_id', "")

            if passed_task_id: 
                with OsirDb() as db:
                    task_info = db.task.get(task_id=passed_task_id)

                trace = task_info.trace

                st.markdown(f"### 🛠️ Task: `{task_info.task_id}`")

                m1, m2 = st.columns([2, 1])
                with m1:
                    st.caption("CASE UUID")
                    st.text(task_info.case_uuid)
                with m2:
                    st.caption("AGENT")
                    st.text(task_info.agent if task_info.agent != 'Null' else "N/A")

                st.divider()

                status_map = {
                    "processing_done": ("✅ SUCCESS", "green"),
                    "processing_failed": ("❌ FAILED", "red"),
                    "processing_started": ("⏳ PROCESSING", "blue"),
                    "task_created": ("🆕 CREATED", "gray")
                }
                status_text, status_color = status_map.get(task_info.processing_status, ("Unknown", "gray"))

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Module", task_info.module)
                with col2:
                    st.metric("Duration", f"{trace.get('duration_seconds', 0):.3f}s")
                with col3:
                    st.metric("Function", trace.get('function', 'N/A'))
                with col4:
                    st.markdown(f"**Status**\n\n:{status_color}[{status_text}]")

                st.write("#### 📂 Context")
                st.info(f"**Input Path:**\n\n`{task_info.input}`")
                st.info(f"**Output Path:**\n\n`{task_info.output}`")

                st.write("#### 📜 Execution Traces")
                logs = trace.get('logs', [])

                if logs:
                    log_content = "\n".join(logs)
                    st.code(log_content, language="log", line_numbers=True)
                else:
                    st.warning("No execution logs available for this task.")

                st.caption(f"Task created: {task_info.timestamp} | Finished: {trace.get('end_time', 'N/A')}")
            else:
                st.info("No Task ID Entered.")

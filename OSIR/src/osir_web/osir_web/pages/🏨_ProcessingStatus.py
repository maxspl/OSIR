import time
import streamlit as st
import pandas as pd
from sqlalchemy import text
from utils.Db import Db_accessor
from streamlit_extras.colored_header import colored_header 
from osir_web.utils import MasterSideBar
from osir_service.postgres.PostgresService import OSIR_DB
from streamlit.components.v1 import html

def color_rows(row):
    if row["processing_status"] == "processing_done":
        return ["background-color: lightgreen; color: gray;"] * len(row)
    elif row["processing_status"] == "processing_failed":
        return ["background-color:  lightcoral; color: lightgray;"] * len(row)
    elif row["processing_status"] == "processing_started":
        return ["background-color:  orange; color: lightgray;"] * len(row)
    else:
        return [""] * len(row)

class ProcessingStatus:
    def __init__(self):
        """
        Initialize the ProcessingStatus class, setting up the database accessor and retrieving cases.
        """
        self.cases: dict = self._get_cases()

    def _get_cases(self):
        return {case[1]: case[0] for case in OSIR_DB.case.list()}
    
    
    def display_ongoing_tasks(self, selected_case_name):
        """
        Display a single table containing data from all DB tables except 'master_status' and 'case_snapshot',
        filtered to display only rows where the column 'processing_status' does not contain 'processing_done'.

        Args:
            selected_case_name (str): The name of the selected case.
            filter_string (str): The string to filter rows by.

        Returns:
            None
        """
        # Collect data from non-empty tables
        st.echo("df")
        tasks = OSIR_DB.task.list(self.cases[selected_case_name])

        if tasks:
            df = pd.DataFrame(tasks)
            uuid_columns = ["case_uuid", "task_id"]
            for col in uuid_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str)

            df.drop(columns=['case_uuid'], inplace=True)
            df.drop(columns=['agent'], inplace=True)

            
            st.dataframe(df,  width='stretch')
        else:
            st.info("No task ongoing")

    def task_by_case(self, selected_case_name, selected_task_status, selected_handler_id, selected_module):
        if selected_case_name:
            tasks_by_case = OSIR_DB.task.list(
                case_uuid=self.cases[selected_case_name],
                processing_status=selected_task_status if selected_task_status else None
            )
            
            if tasks_by_case:
                df = pd.DataFrame(tasks_by_case)
                
                # 1. FIX ARROW SERIALIZATION: Convertir TOUTES les colonnes UUID/Objets en string
                # On boucle sur toutes les colonnes pour éviter l'erreur ArrowInvalid
                for col in df.columns:
                    # Si la colonne contient des objets (comme UUID), on transforme tout en str
                    if df[col].dtype == 'object':
                        df[col] = df[col].apply(lambda x: str(x) if x is not None else "")

                # --- Logique de Filtrage par Handler ---
                if selected_handler_id:
                    handler_info = OSIR_DB.handler.get(handler_id=selected_handler_id)
                    
                    if handler_info and 'task_ids' in handler_info:
                        # Conversion en liste de strings pour matcher avec df["task_id"]
                        target_task_ids = [str(tid) for tid in handler_info['task_ids']]
                        
                        if "task_id" in df.columns:
                            df = df[df["task_id"].isin(target_task_ids)]
                    else:
                        df = pd.DataFrame() 

                # --- Autres Filtres ---
                if selected_module and not df.empty and "module" in df.columns:
                    df = df[df["module"].apply(lambda x: selected_module in x if isinstance(x, list) else x == selected_module)]

                # Nettoyage
                if not df.empty:
                    if 'agent' in df.columns:
                        df.drop(columns=['agent'], inplace=True)
                    
                    # Appliquer le style
                    styled_df = df.style.apply(color_rows, axis=1)
                    
                    event = st.dataframe(
                        styled_df,
                        on_select="rerun",
                        selection_mode="single-cell", # Allows clicking a line
                        hide_index=True,
                        width='stretch'
                    )


                    # Check if a cell was clicked
                    if event.selection.cells:
                        # event.selection.cells[0] is a tuple: (row_index, col_index)
                        selected_cell = event.selection.cells[0] 
                        selected_row_index = selected_cell[0]  # Access the row (first part of tuple)
                        
                        # Retrieve data from the original DataFrame using .iloc
                        selected_row = df.iloc[selected_row_index]
                        
                        previous_task_id = st.session_state.selected_task_id
                        # Save values to session state for Tab 2
                        st.session_state.selected_task_id = str(selected_row["task_id"])
                        # Trigger the JS switch by writing to the placeholder
                        if previous_task_id != selected_row["task_id"]:
                            with js_trigger:
                                html(switch(3), height=0, width=0)

                else:
                    st.info("Aucune tâche ne correspond aux critères sélectionnés.")
            else:
                st.info("Aucune tâche trouvée pour ce cas.")
        else:
            st.info("Veuillez sélectionner un nom de cas.")     
    
    @staticmethod
    def display_task_details(task_info):
        trace = task_info.get('trace', {})
        
        # 1. Top Metadata Header
        st.markdown(f"### 🛠️ Task: `{task_info['task_id']}`")
        
        # Metadata Row 1: Case and IDs
        m1, m2 = st.columns([2, 1])
        with m1:
            st.caption("CASE UUID")
            st.text(task_info['case_uuid'])
        with m2:
            st.caption("AGENT")
            st.text(task_info['agent'] if task_info['agent'] != 'Null' else "N/A")

        st.divider()

        # 2. Key Performance Metrics Row
        status_map = {
            "processing_done": ("✅ SUCCESS", "green"),
            "processing_failed": ("❌ FAILED", "red"),
            "processing_started": ("⏳ PROCESSING", "blue"),
            "task_created": ("🆕 CREATED", "gray")
        }
        status_text, status_color = status_map.get(task_info['processing_status'], ("Unknown", "gray"))

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Module", task_info['module'])
        with col2:
            st.metric("Duration", f"{trace.get('duration_seconds', 0):.3f}s")
        with col3:
            st.metric("Function", trace.get('function', 'N/A'))
        with col4:
            st.markdown(f"**Status**\n\n:{status_color}[{status_text}]")

        # 3. Path & Context (Now always visible)
        st.write("#### 📂 Input Context")
        st.info(f"**Input Path:**\n\n`{task_info['input']}`")

        # 4. Execution Traces (Now always visible)
        st.write("#### 📜 Execution Traces")
        logs = trace.get('logs', [])
        
        if logs:
            # We join the logs with newlines
            log_content = "\n".join(logs)
            
            # Display logs in a scrollable code block for terminal feel
            st.code(log_content, language="log", line_numbers=True)
        else:
            st.warning("No execution logs available for this task.")

        # Optional: Display raw timestamps at the very bottom
        st.caption(f"Task created: {task_info.get('timestamp')} | Finished: {trace.get('end_time', 'N/A')}")
    
    @staticmethod
    def delete_handler_task(case_uuid):
        if case_uuid:
            OSIR_DB.handler.delete(case_uuid=case_uuid)
            OSIR_DB.task.delete(case_uuid=case_uuid)

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

if "switch_count" not in st.session_state:
    st.session_state.switch_count = 0
if "selected_task_id" not in st.session_state:
    st.session_state.selected_task_id = ""
if "selected_handler_id" not in st.session_state:
    st.session_state.selected_handler_id = ""
if "selected_case_name" not in st.session_state:
    st.session_state.selected_case_name = ""
tab1, tab2, tab3, tab4 = st.tabs(["Handler By Case", "Tasks By Case", "Tasks Ongoing" , "Task Logs"])

# 1. Update the function to include a unique timestamp inside the string
def switch(tab_index):
    return f"""
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

with tab1:
    # Utiliser des colonnes pour organiser le header et le bouton Refresh
    header_col1, header_col2 = st.columns([10, 1])

    with header_col1:
        colored_header(
            label="Handler by Cases",
            description="",
            color_name="violet-70",
        )

    with header_col2:
        # Ajouter le bouton Refresh dans la colonne à droite du header
        st.markdown("<br>", unsafe_allow_html=True)  # Ajouter un espace vertical
        if st.button("↻ Refresh", help="Refresh data", width='stretch'):
            st.rerun()

    
    
    processing_status = ProcessingStatus()

    selected_case_name = st.selectbox("Select a case name", [""] + list(processing_status.cases.keys()))

    processing_status_ = st.selectbox(
        "Filtrer par Processing Status (optionnel) :",
        options=["", "processing_started", "processing_done", "processing_failed"]
    )
    exclude_status = st.selectbox(
        "Exclure Processing Status (optionnel) :",
        options=["", "processing_started", "processing_done", "processing_failed"]
    )    

    
    handlers = OSIR_DB.handler.list(
        case_uuid=processing_status.cases[selected_case_name] if selected_case_name else None,
        processing_status=processing_status_ if processing_status_ else None,
        exclude_status=exclude_status if exclude_status else None
    )
    # 2. Use a placeholder to trigger the switch
    js_trigger = st.empty()
    if handlers:
        df = pd.DataFrame(handlers)

        # Convertir les UUID en chaînes pour l'affichage
        uuid_columns = ["handler_id", "case_uuid"]
        for col in uuid_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)

         # Convertir la colonne task_ids (liste d'UUID) en chaînes
        if "task_ids" in df.columns:
            df["task_ids"] = df["task_ids"].apply(
                lambda task_list: [str(task) for task in task_list] if isinstance(task_list, list) else str(task_list)
            )
        
         # Réorganiser les colonnes
        columns_order = ["case_name", "modules", "processing_status"]
        # Ajouter les autres colonnes qui ne sont pas déjà dans columns_order
        other_columns = [col for col in df.columns if col not in columns_order]
        columns_order.extend(other_columns)

        # Réorganiser le DataFrame
        df = df[columns_order]
        # Fonction pour colorer les lignes en fonction du processing_status

        # Appliquer le style
        styled_df = df.style.apply(color_rows, axis=1)

        
        # Afficher le DataFrame
        # st.dataframe(styled_df, width='stretch')
        # 2. Add Row Selection capability
        event = st.dataframe(
            styled_df,
            on_select="rerun",
            selection_mode="single-cell", # Allows clicking a line
            hide_index=True,
            width='stretch'
        )


        # Check if a cell was clicked
        if event.selection.cells:
            # event.selection.cells[0] is a tuple: (row_index, col_index)
            selected_cell = event.selection.cells[0] 
            selected_row_index = selected_cell[0]  # Access the row (first part of tuple)
            
            # Retrieve data from the original DataFrame using .iloc
            selected_row = df.iloc[selected_row_index]
            
            previous_handler_id = st.session_state.selected_handler_id

            # Save values to session state for Tab 2
            st.session_state.selected_case_name = str(selected_row["case_name"])
            st.session_state.selected_handler_id = str(selected_row["handler_id"])
            event = pd.DataFrame()
            # Trigger the JS switch by writing to the placeholder
            if previous_handler_id != selected_row["handler_id"]:
                with js_trigger:
                    html(switch(1), height=0, width=0)
                
            
    else:
        st.info("Aucun handler trouvé.")

    if selected_case_name:
        with st.expander("⚠️ Dangerous action: Clear all tables for this case"):
            st.warning("This will permanently delete all entries in all database tables related to the selected case.")
            confirm_delete = st.checkbox("I understand the consequences and want to proceed with deletion.")

            if st.button("❌ Clear all tables for this case", type="primary", disabled=not confirm_delete):
                with st.spinner(f"Deleting entries for case: {selected_case_name}..."):
                    ProcessingStatus.delete_handler_task(processing_status.cases[selected_case_name])
                st.success(f"✅ All data related to case '{selected_case_name}' was deleted from the database.")

with tab2:
    colored_header(
        label="Tasks By Case",
        description="",
        color_name="violet-70",
    )
    
    processing_status = ProcessingStatus()

    # --- Sync Logic ---
    # Retrieve passed values from session state (with fallbacks)
    passed_case_name = st.session_state.get('selected_case_name', "")
    passed_handler_id = st.session_state.get('selected_handler_id', "")

    # Filtres
    col1, col2, col3, col4 = st.columns(4)        

    with col1:
        case_options = list(processing_status.cases.keys())
        # Find the index of the passed case_name
        try:
            case_index = case_options.index(passed_case_name)
        except ValueError:
            case_index = 0

        selected_case_name = st.selectbox(
            "Case name", 
            case_options, 
            index=case_index
        )

    with col2:
        # Récupérer la liste des handler_id pour le cas sélectionné
        handlers = OSIR_DB.handler.list(case_uuid=processing_status.cases[selected_case_name])
        handler_ids = [str(handler["handler_id"]) for handler in handlers]
        
        # Options include an empty string at the beginning
        all_handler_options = [""] + handler_ids
        
        # Find the index of the passed handler_id
        try:
            handler_index = all_handler_options.index(passed_handler_id)
        except ValueError:
            handler_index = 0

        selected_handler_id = st.selectbox(
            "Handler ID", 
            all_handler_options, 
            index=handler_index
        )

    with col3:
        task_status_options = ["", "processing_started", "processing_done", "processing_failed"]
        selected_task_status = st.selectbox("Task status", task_status_options)
        
    with col4:
        # Fetch modules for the selected case
        task_list = OSIR_DB.task.list(case_uuid=processing_status.cases[selected_case_name])
        modules = list(set([str(t['module']) for t in task_list]))
        selected_module = st.selectbox("Module", [""] + modules)

    # --- Display Results ---
    processing_status.task_by_case(
        selected_case_name=selected_case_name,
        selected_task_status=selected_task_status,
        selected_handler_id=selected_handler_id,
        selected_module=selected_module
    )  

    # Bouton Refresh
    if st.button("Refresh", width='stretch'):
        if selected_case_name:
            processing_status.task_by_case(
                selected_case_name=selected_case_name,
                selected_task_status=selected_task_status
            )

with tab3:
    colored_header(
        label="All Tasks",
        description="",
        color_name="violet-70",
    )

    st.echo("df")
    tasks = OSIR_DB.task.list(processing_status=["task_created", "processing_pending", "processing_started"])

    if tasks:
        df = pd.DataFrame(tasks)
        uuid_columns = ["case_uuid", "task_id"]
        for col in uuid_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)

        df.drop(columns=['agent'], inplace=True)       
        st.dataframe(df,  width='stretch')
    else:
        st.info("No task Found")

with tab4:
    colored_header(
        label="Taks Logs",
        description="",
        color_name="violet-70",
    )
    
    passed_task_id = st.session_state.get('selected_task_id', "")
    info = OSIR_DB.task.get(task_id=passed_task_id)
    if info:
        ProcessingStatus.display_task_details(info)


# Sidebar
MasterSideBar.sidebar()



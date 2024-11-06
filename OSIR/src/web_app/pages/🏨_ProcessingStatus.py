import streamlit as st
import pandas as pd
from sqlalchemy import text
from utils.Db import Db_accessor
from streamlit_extras.colored_header import colored_header 
from src.web_app.utils import MasterSideBar


# Database formatter class
class ProcessingStatus:
    def __init__(self):
        """
        Initialize the ProcessingStatus class, setting up the database accessor and retrieving cases.
        """
        self.db_accessor = Db_accessor()
        self.cases = self._get_cases()
        
    def _get_cases(self):
        """
        Retrieve distinct case paths from all tables in the database.

        Returns:
            list: A list of unique case names derived from the case paths.
        """
        # Query to get all distinct case paths from all tables
        case_names = set()
        with self.db_accessor.engine.connect() as conn:
            tables_query = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = conn.execute(tables_query)
            for table in tables:
                table_name = table[0]
                case_path_query = text(f"SELECT DISTINCT case_path FROM {table_name}")
                result = conn.execute(case_path_query)
                for row in result:
                    case_path = row[0]
                    case_name = case_path.split('/')[-1]  # Get the last element of the path
                    case_names.add(case_name)
        return list(case_names)
    
    def display_DB_tables(self, selected_case_name, filter_string):
        """
        Display non-empty tables containing data for the selected case name, optionally filtered by a string.

        Args:
            selected_case_name (str): The name of the selected case.
            filter_string (str): The string to filter rows by.

        Returns:
            None
        """
        # Collect non-empty tables
        non_empty_tables = []
        table_data = {}

        with self.db_accessor.engine.connect() as conn:
            tables_query = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = conn.execute(tables_query)
            table_names = [table[0] for table in tables]

            for table_name in table_names:
                if table_name == "master_status":
                    continue
                query = text(f"SELECT * FROM {table_name} WHERE case_path LIKE :case_path")
                params = {"case_path": f"%/{selected_case_name}"}
                
                if filter_string:
                    query = text(f"SELECT * FROM {table_name} WHERE case_path LIKE :case_path AND (CAST({table_name} AS TEXT) LIKE :filter_string)")
                    params["filter_string"] = f"%{filter_string}%"
                
                df = pd.read_sql(query, con=self.db_accessor.engine, params=params)
                
                if not df.empty:
                    non_empty_tables.append(table_name)
                    table_data[table_name] = df

        # Create tabs for non-empty tables only
        if non_empty_tables:
            tabs = st.tabs(non_empty_tables)

            for tab, table_name in zip(tabs, non_empty_tables):
                with tab:
                    st.dataframe(table_data[table_name], use_container_width=True)

    def display_ongoing_tasks(self, selected_case_name):
        """
        Display a single table containing data from all DB tables except 'master_status',
        filtered to display only rows where the column 'processing_status' does not contain 'processing_done'.

        Args:
            selected_case_name (str): The name of the selected case.
            filter_string (str): The string to filter rows by.

        Returns:
            None
        """
        # Collect data from non-empty tables
        st.echo("df")
        table_data = []

        with self.db_accessor.engine.connect() as conn:
            tables_query = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = conn.execute(tables_query)
            table_names = [table[0] for table in tables]

            for table_name in table_names:
                if table_name == "master_status":
                    continue

                query = text(f"SELECT * FROM {table_name} WHERE case_path LIKE :case_path")
                params = {"case_path": f"%/{selected_case_name}"}
                
                df = pd.read_sql(query, con=self.db_accessor.engine, params=params)
                
                if not df.empty:
                    if 'processing_status' in df.columns:
                        df = df[df['processing_status'] != 'processing_done']
                    if not df.empty:
                        df.drop(columns=['case_uuid'], inplace=True)
                        df.drop(columns=['id'], inplace=True)
                        df.insert(0, 'table_name', table_name)
                        table_data.append(df)
        
        # Combine data from all tables into a single DataFrame
        if table_data:
            combined_df = pd.concat(table_data, ignore_index=True)
            st.dataframe(combined_df, use_container_width=True)
        else:
            st.info("No task ongoing")


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

tab1, tab2 = st.tabs(["Detailed Processing Status", "Tasks ongoing"])

with tab1:
    colored_header(
        label="Tables containing processed data",
        description="",
        color_name="violet-70",
    )

    processing_status = ProcessingStatus()

    # Create a selectbox for the user to choose a case name
    selected_case_name = st.selectbox("Select a case name", processing_status.cases)

    # Text input for filtering
    filter_string = st.text_input("Filter rows containing")

    # Display the DB tables
    processing_status.display_DB_tables(selected_case_name, filter_string)

with tab2:
    colored_header(
        label="Tasks ongoing",
        description="",
        color_name="violet-70",
    )
    
    processing_status = ProcessingStatus()

    # Create a selectbox for the user to choose a case name
    selected_case_name = st.selectbox("Select a case name ", processing_status.cases)

    # processing_status.display_ongoing_tasks(selected_case_name)

    st.button("Refresh", on_click=processing_status.display_ongoing_tasks(selected_case_name), use_container_width=True)

# Sidebar
MasterSideBar.sidebar()



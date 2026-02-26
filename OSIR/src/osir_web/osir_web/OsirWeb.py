from osir_lib.core.model.OsirProfileModel import OsirProfileModel
from osir_lib.core.model.OsirModuleModel import OsirModuleModel

import streamlit as st
import os
import yaml
import concurrent.futures
import pandas as pd

from streamlit_extras.colored_header import colored_header
from osir_web.utils import OsirWebSidebar

from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.core.FileManager import FileManager
from osir_lib.logger.logger import AppLogger
from osir_lib.core.OsirInput import OsirInput
from osir_service.watchdog.MonitorCase import MonitorCase

from osir_web.pages.OsirWebCase import OsirWebCase
from osir_web.pages.OsirWebFile import OsirWebFile
from osir_web.pages.OsirWebHelper import OsirWebHelper
from osir_web.pages.OsirWebTask import OsirWebTask
from osir_web.pages.OsirWebMonitoring import OsirWebMonitoring
from osir_web.pages.OsirWebFlower import OsirWebFlower
from osir_web.pages.OsirWebDoc import OsirWebDoc
from osir_web.pages.OsirWebBug import OsirWebBug
from osir_web.pages.OsirWebApiDoc import OsirWebApiDoc

logger = AppLogger().get_logger()

class OsirWeb:
    def __init__(self):
        st.set_page_config(
            page_title="OSIR - Orchestration Software for Incident Response",
            page_icon="⚙️",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                "Get help": "https://github.com/maxspl/OSIR",
                "Report a bug": "https://github.com/maxspl/OSIR",
                "About": "OSIR"
            }
        )
        

    def render(self):
        # Map page titles to callable functions
        navigation = {
            '🛠️ Orchestrator': [
                st.Page(OsirWebCase.render, title="Case Orchestration", url_path='OsirWebCase'),
                st.Page(OsirWebFile.render, title="File Orchestration", url_path='OsirWebFile'),
                st.Page(OsirWebHelper.render, title="Helper", url_path='OsirWebHelper')
            ],
            '📡 Status': [
                st.Page(OsirWebTask.render, title="Task On-Going", url_path='OsirWebTask'),
                st.Page(OsirWebMonitoring.render, title="Orchestration Monitoring", url_path='OsirWebMonitoring'),
                st.Page(OsirWebFlower.render, title="Flower Monitoring", url_path='OsirWebFlower'),
            ],
            '❓ Bug & Help': [
                st.Page(OsirWebDoc.render, title="OSIR Documentation", url_path='OsirWebDoc'),
                st.Page(OsirWebApiDoc.render, title="API Documentation", url_path='OsirWebApiDoc'),
                st.Page(OsirWebBug.render, title="Bug & GitHub", url_path='OsirWebBug')
            ]
        }
        pg = st.navigation(navigation)
        

            # For widget persistence, we need always copy the session state to itself, being careful with widgets that cannot be persisted, like st.data_editor() (where we use the "__do_not_persist" suffix to avoid persisting it)
        for key in st.session_state.keys():
            if not key.endswith('__do_not_persist'):
                st.session_state[key] = st.session_state[key]

        # This is needed for the st.dataframe_editor() class (https://github.com/andrew-weisman/streamlit-dataframe-editor) but is useful for seeing where we are and where we've been
        st.session_state['url_path'] = pg.url_path if pg.url_path != '' else 'Home'
        if 'url_path_prev' not in st.session_state:
            st.session_state['url_path_prev'] = st.session_state['url_path']

        # On every page, display its title
        # st.title(pg.title)

        # Render the select page
        
        pg.run()

        OsirWebSidebar.sidebar()

        # Update the previous page location
        st.session_state['url_path_prev'] = st.session_state['url_path']

if __name__ == "__main__":
    app = OsirWeb()
    app.render()





# if __name__ == "__main__":
#     app = ConfigurationApp()
#     st.set_page_config(
#         page_title="OSIR",
#         layout="wide",
#         initial_sidebar_state="expanded",
#         menu_items={
#             "Get help": "https://github.com/maxspl/OSIR",
#             "Report a bug": "https://github.com/maxspl/OSIR",
#             "About": "OSIR"
#         }
#     )
#     app.run()
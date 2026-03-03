
import streamlit as st

from osir_web.utils import OsirWebSidebar

from osir_lib.logger.logger import AppLogger

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

        pg.run()
        
        OsirWebSidebar.sidebar()


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
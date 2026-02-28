from osir_web.pages.OsirWebHeader import OsirWebHeader
import streamlit.components.v1 as components
from osir_lib.core.OsirAgentConfig import OsirAgentConfig


class OsirWebApiDoc:
    @staticmethod
    def render():
        OsirWebHeader.render(
            title="OSIR - Documentation",
            subtitle="Learn how to use OSIR API !",
        )
        try:
            master_host = OsirAgentConfig().master_host
        except FileNotFoundError:
            master_host = "localhost"

        components.iframe(
            src=f"http://{master_host}:8502/docs",
            height=750,
            scrolling=True
        )
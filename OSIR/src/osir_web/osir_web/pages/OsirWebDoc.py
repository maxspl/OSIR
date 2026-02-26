import streamlit as st
from osir_web.pages.OsirWebHeader import OsirWebHeader
import streamlit.components.v1 as components
class OsirWebDoc:
    @staticmethod
    def render():
        OsirWebHeader.render(
            title="OSIR - Documentation",
            subtitle="Learn how to use OSIR !",
        )
        components.iframe(
        src="https://osir.readthedocs.io/en/latest/",
        height=750,
        scrolling=True
        )
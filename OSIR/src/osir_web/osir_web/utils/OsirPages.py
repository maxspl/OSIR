import streamlit as st

from osir_web.pages.OsirWebCase import OsirWebCase
from osir_web.pages.OsirWebFile import OsirWebFile
from osir_web.pages.OsirWebHelper import OsirWebHelper
from osir_web.pages.OsirWebTask import OsirWebTask
from osir_web.pages.OsirWebMonitoring import OsirWebMonitoring
from osir_web.pages.OsirWebFlower import OsirWebFlower
from osir_web.pages.OsirWebDoc import OsirWebDoc
from osir_web.pages.OsirWebBug import OsirWebBug
from osir_web.pages.OsirWebApiDoc import OsirWebApiDoc

class OsirPages:
    # 🛠️ Orchestrator
    page_case = st.Page(
        OsirWebCase.render,
        title="Case Orchestration",
        url_path="OsirWebCase",
    )
    page_file = st.Page(
        OsirWebFile.render,
        title="File Orchestration",
        url_path="OsirWebFile",
    )
    page_helper = st.Page(
        OsirWebHelper.render,
        title="Helper",
        url_path="OsirWebHelper",
    )

    # 📡 Status
    page_task = st.Page(
        OsirWebTask.render,
        title="Task On-Going",
        url_path="OsirWebTask",
    )
    page_monitoring = st.Page(
        OsirWebMonitoring.render,
        title="Orchestration Monitoring",
        url_path="OsirWebMonitoring",
    )
    page_flower = st.Page(
        OsirWebFlower.render,
        title="Flower Monitoring",
        url_path="OsirWebFlower",
    )

    # ❓ Bug & Help
    page_doc = st.Page(
        OsirWebDoc.render,
        title="OSIR Documentation",
        url_path="OsirWebDoc",
    )
    page_api_doc = st.Page(
        OsirWebApiDoc.render, title="API Documentation", url_path="OsirWebApiDoc",
    )
    page_bug = st.Page(
        OsirWebBug.render, title="Bug & GitHub", url_path="OsirWebBug",
    )

    navigation = {
        "🛠️ Orchestrator": [page_case, page_file, page_helper],
        "📡 Status": [page_task, page_monitoring, page_flower],
        "❓ Bug & Help": [page_doc, page_api_doc, page_bug],
    }
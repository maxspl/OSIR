import os

import streamlit as st

from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_web.pages.OsirWebHeader import OsirWebHeader


class OsirWebHelper:
    @staticmethod
    def render():
        """
            Auxiliary tab to quickly view the content of profiles and modules.
            Helpful for understanding what's configured without leaving the UI.
        """
        OsirWebHeader.render(
            title="OSIR - Helper Modules & Profiles",
            subtitle="Find the configuration of Profiles & Modules")

        helper_choice = st.selectbox("Choose to display content of a Profile or Module", ["Profile", "Module"])

        if helper_choice == "Profile":
            helper_profile = st.selectbox("Select Profile", FileManager.get_yaml_files(str(OSIR_PATHS.PROFILES_DIR), relative=True))
            if helper_profile:
                profile_path = os.path.join(OSIR_PATHS.PROFILES_DIR, helper_profile)
                profile_content = FileManager.load_yaml_file(profile_path)
                st.json(profile_content)

        if helper_choice == "Module":
            
            helper_module = st.selectbox("Select Module", FileManager.resolve_modules_parent_dir(FileManager.get_yaml_files(OSIR_PATHS.MODULES_DIR)))
            if helper_module:
                module_path = os.path.join(OSIR_PATHS.MODULES_DIR, helper_module)
                module_content = FileManager.load_yaml_file(module_path)
                st.json(module_content)
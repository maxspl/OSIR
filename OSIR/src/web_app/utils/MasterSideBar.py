import streamlit as st
import os
import psutil
import subprocess
from streamlit_extras.colored_header import colored_header
from src.utils.AgentConfig import AgentConfig
from src.web_app.utils import StaticVars
from streamlit_js_eval import get_page_location
import time


class SystemManager:
    def __init__(self, key=""):
        self.location_details = get_page_location(component_key=key)
        time.sleep(2)
        self.host = self.location_details["hostname"]
        
    @staticmethod
    def get_host_specs():
        """
        Retrieve host specifications such as CPU count, RAM, and disk usage.

        Returns:
            dict: A dictionary containing the host's CPU count, RAM, and disk usage details.
        """
        specs = {
            "CPU Count": psutil.cpu_count(logical=True),
            "RAM": psutil.virtual_memory().total / (1024 ** 3),  # Convert bytes to GB
            "Disk Total": psutil.disk_usage('/').total / (1024 ** 3),  # Convert bytes to GB
            "Disk Used": psutil.disk_usage('/').used / (1024 ** 3),  # Convert bytes to GB
            "Disk Free": psutil.disk_usage('/').free / (1024 ** 3),  # Convert bytes to GB
        }
        return specs

    @staticmethod
    def get_directory_size(directory):
        """
        Get total size of files in a specific directory using subprocess.

        Args:
            directory (str): The directory to calculate the total size.

        Returns:
            float: The total size of the directory in gigabytes.
        """
        # Command to calculate the size of the directory using 'du'
        command = ["du", "-sh", directory]

        # Run the command and capture the output
        result = subprocess.run(command, capture_output=True, text=True)

        # Extract stdout and remove directory (result of du is 'size\t<directory> )
        size = result.stdout.split("\t")[0]
        return size
            

def sidebar():
    """Set up and display the sidebar with host specifications and cases usage."""
    
    with st.sidebar:
        
        # External links to DB and Splunk

        # location_details = get_page_location()
        # time.sleep(1)
        # host = location_details["hostname"]
        host = SystemManager().host

        # Get splunk host
        agent_config = AgentConfig()
        splunk_host = agent_config.splunk_host if agent_config.splunk_host not in ["host.docker.internal", "127.0.0.1"] else host

        # Set the URL for the iframe
        url = f"http://{host}:80/"
        splunk_url = f"http://{splunk_host}:8000/"
        colored_header(
            label="Useful links",
            description="",
            color_name="red-70",
        )
        with st.expander(":round_pushpin: External"):
            st.page_link(url, label="Open Database", help="open a new tab to pgadmin", use_container_width=True, icon="💾")
            st.page_link(splunk_url, label="Splunk", help="open a new tab to local Splunk server", use_container_width=True, icon="💹")
        
        # Master specs
        colored_header(
            label="Master Specifications",
            description=" ",
            color_name="green-70",
        )
        
        specs = SystemManager.get_host_specs()
        st.write(f"**Master host:** {os.getenv('HOST_HOSTNAME', '')}")
        st.write(f"**CPU Count:** {specs['CPU Count']}")
        st.write(f"**RAM:** {specs['RAM']:.2f} GB")
        st.write(f"**Disk Total:** {specs['Disk Total']:.2f} GB")
        st.write(f"**Disk Used:** {specs['Disk Used']:.2f} GB")
        st.write(f"**Disk Free:** {specs['Disk Free']:.2f} GB")
        
        if (specs['Disk Free'] / specs['Disk Total']) < 0.1:
            st.error("Warning: Disk free space is less than 10% of the total disk space!")

        colored_header(
            label="Cases Usage (/OSIR/share/cases)",
            description=" ",
            color_name="green-70",
        )
        
        cases_usage = SystemManager.get_directory_size(StaticVars.CASES_DIR)
        st.write(f"**Used:** {cases_usage}")
        
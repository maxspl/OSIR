import streamlit as st
import os
import yaml
import concurrent.futures
from streamlit_extras.colored_header import colored_header
from src.utils.BaseProfile import BaseProfile
from src.tasks import task_manager
from src.monitor import MonitorCase
from src.log.logger_config import AppLogger
from src.web_app.utils import MasterSideBar
from src.web_app.utils import StaticVars

logger = AppLogger(__name__).get_logger()


class FileManager:
    @staticmethod
    def resolve_modules_parent_dir(modules):
        """
        Convert a list of modules to a list of their relative paths from a base directory.

        Args:
            modules (list): A list of module file names.

        Returns:
            list: A list of relative paths for the modules found in the base directory.
        """
        MODULES_DIR = "/OSIR/OSIR/configs/modules/"
        paths = []
        for root, _, files in os.walk(MODULES_DIR):
            for file in files:
                for module in modules:
                    if file == module:
                        # Get the relative path by removing the MODULES_DIR part from the full path
                        relative_path = os.path.relpath(os.path.join(root, file), MODULES_DIR)
                        paths.append(relative_path)
        return paths

    @staticmethod
    def get_yaml_files(directory):
        """
        Get a list of .yml files in a given directory recursively.

        Args:
            directory (str): The directory to search for .yml files.

        Returns:
            list: A list of .yml files found in the directory.
        """
        yaml_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.yml'):
                    # yaml_files.append(os.path.relpath(os.path.join(root, file), directory))
                    yaml_files.append(file)
        return yaml_files

    @staticmethod
    def get_cases(directory):
        """
        Get a list of directories in a given directory.

        Args:
            directory (str): The directory to search for subdirectories.

        Returns:
            list: A list of subdirectories found in the directory.
        """
        return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

    @staticmethod
    def load_yaml_file(filepath):
        """
        Load content from a YAML file.

        Args:
            filepath (str): The path to the YAML file.

        Returns:
            dict: The content of the YAML file.
        """
        with open(filepath, 'r') as file:
            return yaml.safe_load(file)


# class SystemManager:
#     @staticmethod
#     def get_host_specs():
#         """
#         Retrieve host specifications such as CPU count, RAM, and disk usage.

#         Returns:
#             dict: A dictionary containing the host's CPU count, RAM, and disk usage details.
#         """
#         specs = {
#             "CPU Count": psutil.cpu_count(logical=True),
#             "RAM": psutil.virtual_memory().total / (1024 ** 3),  # Convert bytes to GB
#             "Disk Total": psutil.disk_usage('/').total / (1024 ** 3),  # Convert bytes to GB
#             "Disk Used": psutil.disk_usage('/').used / (1024 ** 3),  # Convert bytes to GB
#             "Disk Free": psutil.disk_usage('/').free / (1024 ** 3),  # Convert bytes to GB
#         }
#         return specs

#     @staticmethod
#     def get_directory_size(directory):
#         """
#         Get total size of files in a specific directory.

#         Args:
#             directory (str): The directory to calculate the total size.

#         Returns:
#             float: The total size of the directory in gigabytes.
#         """
#         total_size = 0
#         for dirpath, dirnames, filenames in os.walk(directory):
#             for f in filenames:
#                 fp = os.path.join(dirpath, f)
#                 # Skip if it is symbolic link
#                 if not os.path.islink(fp):
#                     total_size += os.path.getsize(fp)
#         return total_size / (1024 ** 3)


class ConfigurationApp:

    def __init__(self):
        self.PROFILES_DIR = StaticVars.PROFILES_DIR
        self.MODULES_DIR = StaticVars.MODULES_DIR
        self.CASES_DIR = StaticVars.CASES_DIR
        self.profiles = FileManager.get_yaml_files(self.PROFILES_DIR)
        self.modules = FileManager.get_yaml_files(self.MODULES_DIR)
        self.cases = FileManager.get_cases(self.CASES_DIR)

        self.modules_w_parentdir = FileManager.resolve_modules_parent_dir(self.modules)

    @staticmethod
    def comma_separated_strings(value):
        """
        Converts a comma-separated string into a list of strings, ensuring each item has a '.yml' extension.

        Args:
            value (str): The comma-separated string.

        Returns:
            list: A list of strings with '.yml' extensions.
        """
        if not value:
            return []
        items = [item.strip() for item in value.split(',')]
        items_with_yml = [item + ".yml" if not item.endswith(".yml") else item for item in items]
        return items_with_yml

    def run(self):
        """
        Main method to run the ConfigurationApp, setting up the UI with tabs and calling the respective methods.
        """
        colored_header(
            label="Case processor",
            description=" ",
            color_name="violet-70",
        )

        tabs = st.tabs(["Main", "Helper"])

        with tabs[0]:
            self.main_tab()

        with tabs[1]:
            self.helper_tab()

        MasterSideBar.sidebar()

    def main_tab(self):
        """
        Method to set up and handle the main tab in the UI.
        """
        selected_profile = st.selectbox("Profile", [""] + self.profiles, help="Select a profile.")
        if selected_profile:
            selected_modules = []
        else:

            selected_modules_w_parentdir = st.multiselect("Modules", self.modules_w_parentdir, help="Select specific modules to be exclusively used.")
            selected_modules = [os.path.basename(module) for module in selected_modules_w_parentdir]
        module_add = module_remove = []

        if selected_profile:
            profile_path = os.path.join(self.PROFILES_DIR, selected_profile)
            profile_content = FileManager.load_yaml_file(profile_path)
            if 'modules' in profile_content:
                profile_modules = [
                    module + ".yml" if not module.endswith('.yml') else module for module in profile_content['modules']
                ]
                modules_without_parentdir = [os.path.basename(module) for module in self.modules]
                selected_modules = [module for module in profile_modules if module in modules_without_parentdir]  # Keep existing modules

            module_add = st.multiselect("Add Modules", self.modules_w_parentdir, help="Add specific modules to the list.")
            module_remove = st.multiselect("Remove Modules", self.modules_w_parentdir, help="Remove specific modules from the list.")

        selected_case = st.selectbox("Case", self.cases, help="Select a case directory.")
        if not self.cases:
            st.warning("No cases found in /OSIR/share/cases/.")

        if st.button("Submit"):
            logger.debug("Module ADD" + str(module_add))
            self.process_submission(selected_profile, selected_modules, module_add, module_remove, selected_case)

    def helper_tab(self):
        """
        Method to set up and handle the helper tab in the UI.
        """
        st.title("Helper")
        helper_choice = st.selectbox("Choose to display content of a Profile or Module", ["Profile", "Module"])

        if helper_choice == "Profile":
            helper_profile = st.selectbox("Select Profile", self.profiles)
            if helper_profile:
                profile_path = os.path.join(self.PROFILES_DIR, helper_profile)
                profile_content = FileManager.load_yaml_file(profile_path)
                st.write(profile_content)

        if helper_choice == "Module":
            helper_module = st.selectbox("Select Module", self.modules_w_parentdir)
            if helper_module:
                module_path = os.path.join(self.MODULES_DIR, helper_module)
                module_content = FileManager.load_yaml_file(module_path)
                st.write(module_content)

    # def sidebar(self):
    #     """Set up and display the sidebar with host specifications and cases usage."""
    #     with st.sidebar:
    #         colored_header(
    #             label="Master Specifications",
    #             description=" ",
    #             color_name="violet-70",
    #         )
    #         specs = SystemManager.get_host_specs()
    #         st.write(f"**Master host:** {os.getenv('HOST_HOSTNAME', '')}")
    #         st.write(f"**CPU Count:** {specs['CPU Count']}")
    #         st.write(f"**RAM:** {specs['RAM']:.2f} GB")
    #         st.write(f"**Disk Total:** {specs['Disk Total']:.2f} GB")
    #         st.write(f"**Disk Used:** {specs['Disk Used']:.2f} GB")
    #         st.write(f"**Disk Free:** {specs['Disk Free']:.2f} GB")

    #         if (specs['Disk Free'] / specs['Disk Total']) < 0.1:
    #             st.error("Warning: Disk free space is less than 10% of the total disk space!")

    #         colored_header(
    #             label="Cases Usage (/OSIR/share/cases)",
    #             description=" ",
    #             color_name="violet-70",
    #         )
    #         cases_usage = SystemManager.get_directory_size(self.CASES_DIR)
    #         st.write(f"**Used:** {cases_usage:.2f} GB")

    def process_submission(self, selected_profile, selected_modules, module_add, module_remove, selected_case):
        """
        Process the input values and initiate the processing job.

        Args:
            selected_profile (str): The selected profile name.
            selected_modules (list): A list of selected module names.
            module_add (str): Comma-separated string of modules to add.
            module_remove (str): Comma-separated string of modules to remove.
            selected_case (str): The selected case directory.

        Returns:
            None
        """
        # Process the input values
        modules_to_add = module_add
        modules_to_remove = module_remove

        # Validate inputs similar to the original argparse checks
        if not selected_profile and not selected_modules:
            st.error("At least one of profile or module must be specified.")
            return

        if (modules_to_add or modules_to_remove) and not selected_profile:
            st.error("module_add or module_remove can only be used when a profile is specified.")
            return

        if (selected_profile or selected_modules) and not selected_case:
            st.error("case must be set when using profile or module.")
            return

        case_path = os.path.join(self.CASES_DIR, selected_case)
        if not os.path.isdir(case_path):
            st.error(f"You selected a case that does not exist. Verify that {case_path} is the right path to process")
            return

        profile_instance = BaseProfile(selected_profile) if selected_profile else None

        # Debugging: Print or log the modules being processed
        logger.debug(f"Processing job with profile: {selected_profile}")
        logger.debug(f"Selected modules: {selected_modules}")
        logger.debug(f"Modules to add: {modules_to_add}")
        logger.debug(f"Modules to remove: {modules_to_remove}")
        logger.debug(f"Case path: {case_path}")

        try:
            job = task_manager.ProcessorJob(
                case_path, profile_instance, selected_modules, modules_to_add, modules_to_remove
            )
        except FileNotFoundError as e:
            st.error(f"Error creating ProcessorJob: {e}")
            logger.error(f"Error creating ProcessorJob: {e}")
            return

        modules_selected = job._get_modules_selected()

        # Used only for display, given more information with the module parent dir inside modules dir
        module_w_parentdir = FileManager.resolve_modules_parent_dir(modules_selected)
        modules_selected_str = "\n".join([f"- {module}" for module in module_w_parentdir])

        # Display the selected modules in a better format
        st.info(f"Modules selected:\n\n{modules_selected_str}")

        monitor_case = MonitorCase.MonitorCase(case_path, modules_selected)

        # Use ThreadPoolExecutor to run the setup_handler in the background
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        executor.submit(monitor_case.setup_handler)

        st.success("Processing started.")
        # Provide a link to the processing status page
        st.page_link("pages/🏨_ProcessingStatus.py", label="Processing status", icon="🏨")


if __name__ == "__main__":
    app = ConfigurationApp()
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
    app.run()

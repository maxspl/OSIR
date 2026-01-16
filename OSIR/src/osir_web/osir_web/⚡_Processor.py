from osir_lib.core.model.OsirProfileModel import OsirProfileModel
import streamlit as st
import os
import yaml
import concurrent.futures
import pandas as pd

from code_editor import code_editor
from streamlit_extras.colored_header import colored_header
from osir_web.utils import MasterSideBar

from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.core.FileManager import FileManager
from osir_lib.logger.logger import AppLogger
from osir_lib.core.OsirInput import OsirInput
from osir_service.watchdog.MonitorCase import MonitorCase


logger = AppLogger().get_logger()


class ConfigurationApp:
    """
    Streamlit application for selecting profiles/modules, editing module configurations
    in-memory, and launching processing on selected cases/files.
    """

    def __init__(self):
        """
        Initialize configuration paths, discover profiles/modules/cases, and set up
        an in-memory store for edited module YAMLs that persists across reruns.
        """
        self.PROFILES_DIR = OSIR_PATHS.PROFILES_DIR
        self.MODULES_DIR = OSIR_PATHS.MODULES_DIR
        self.CASES_DIR = OSIR_PATHS.CASES_DIR
        self.profiles = FileManager.get_yaml_files(self.PROFILES_DIR, relative=True)
        self.modules = FileManager.get_yaml_files(self.MODULES_DIR)
        self.cases = FileManager.get_cases(self.CASES_DIR)
        self.modules_w_parentdir = FileManager.resolve_modules_parent_dir(self.modules)

        # Persist edits across reruns
        if "edited_modules" not in st.session_state:
            st.session_state["edited_modules"] = {}
        self.edited_modules: dict[str, str] = st.session_state["edited_modules"]

    @staticmethod
    def comma_separated_strings(value):
        """
        Converts a comma-separated string into a list of strings, ensuring each item has a '.yml' extension.

        Args:
            value (str): The comma-separated string.

        Returns:
            list[str]: A list of strings with '.yml' extensions.
        """
        if not value:
            return []
        items = [item.strip() for item in value.split(',')]
        items_with_yml = [item + ".yml" if not item.endswith(".yml") else item for item in items]
        return items_with_yml

    def run(self):
        """
        Entry point for the Streamlit app. Renders tabs and master sidebar content.
        """
        colored_header(
            label="Case processor",
            description=" ",
            color_name="violet-70",
        )

        tabs = st.tabs(["Main", "Apply Module", "Helper"])

        with tabs[0]:
            self.main_tab()

        with tabs[2]:
            self.helper_tab()

        with tabs[1]:
            self.module_applier()

        MasterSideBar.sidebar()

    def display_module_editors(self, selected_modules: list[str]) -> None:
        """
        Render an editor for the provided module(s). Intended to be called with
        a single module at a time for a no-scrolling UX.

        Notes:
            - Edits are stored in-memory only (self.edited_modules + st.session_state).
            - The underlying YAML files on disk are NOT modified.
            - Uses a guard to ignore transient empty values emitted by the editor when switching.

        Args:
            selected_modules (list[str]): List of module basenames to edit (e.g., ["foo.yml"]).
        """
        for module_name in selected_modules or []:
            # Find the relative path inside configs/modules for this basename
            rel_path = None
            for rel in self.modules_w_parentdir:
                if os.path.basename(rel) == module_name:
                    rel_path = rel
                    break
            if not rel_path:
                continue

            full_path = os.path.join(self.MODULES_DIR, rel_path)
            try:
                content_dict = FileManager.load_yaml_file(full_path)
                original = yaml.safe_dump(content_dict, sort_keys=False)
            except Exception as e:
                original = f"# Error loading YAML for {module_name}: {e}"

            # Per-module editor buffer in session state
            state_key = f"mod_yaml__{module_name}"
            if state_key not in st.session_state:
                st.session_state[state_key] = self.edited_modules.get(module_name, original)

            st.write(f"### ✏️ Edit configuration for `{module_name}`")

            # Render editor from our buffer; code_editor returns a dict with "text"
            result = code_editor(
                st.session_state[state_key],
                lang="yaml",
                height=[20, 36],   # min/max visible line counts
                theme="vs-dark",
                key=f"code_editor__{module_name}",
            )

            new_text = result.get("text") if isinstance(result, dict) else None

            # Commit only meaningful updates (avoid accidental wipe when editor emits "")
            if new_text is not None:
                if new_text != st.session_state[state_key] and not (new_text == "" and st.session_state[state_key] != ""):
                    st.session_state[state_key] = new_text
                    self.edited_modules[module_name] = new_text

            # Live YAML validation of the current buffer
            try:
                yaml.safe_load(st.session_state[state_key])
                st.caption("✅ YAML valid")
            except Exception as e:
                st.error(f"YAML error: {e}")

            st.divider()

    def module_applier(self):
        """
        UI to run exactly one module on a user-selected file of a case.
        Optionally allows editing that module's configuration in-memory before running.
        """
        st.title("Apply Module")

        st.write(
            "This section allows you to apply a specific module to a file. "
            "Select a case, then a file, and finally a module, then start the action."
        )

        # Case selection (prefixed with an empty choice)
        selected_case = st.selectbox("Case", [""] + self.cases, help="Select a case directory.", key="apply_file")

        # Only show file dropdown if a case is selected
        if selected_case:
            files_in_case = FileManager.get_files_in_cases(os.path.join(self.CASES_DIR, selected_case))
            file = st.selectbox("File", [""] + files_in_case, help="Select a file to apply the module to.")
        else:
            file = None  # In case no file is selected

        selected_modules = []
        if file:
            module = st.selectbox("Module", [""] + self.modules_w_parentdir, help="Pick exactly one module to run/edit.")
            selected_modules = [os.path.basename(module)] if module else []

            # Single-module editor flow (optional)
            if selected_modules and st.checkbox("Edit this module's configuration (optional)"):
                self.display_module_editors([selected_modules[0]])

        # Action button
        if st.button("Submit "):
            self.process_submission_file(selected_modules, selected_case, file)

    def main_tab(self):
        """
        Main UI for selecting profiles and/or modules, optionally editing the selected
        modules' configurations (in-memory), and launching processing on a case.
        """
        st.subheader("Select Modules")

        selected_profile = st.selectbox("Profile", [""] + self.profiles, help="Select a profile.")
        use_table_view = st.toggle("🔁 Switch to table view for module selection", value=False)

        selected_modules = []
        module_add = module_remove = []

        if selected_profile:
            profile_path = os.path.join(self.PROFILES_DIR, selected_profile)
            profile_content = FileManager.load_yaml_file(profile_path)

            # -- modules declared in the profile (basename, always ending in .yml) ------
            profile_modules = [
                m + ".yml" if not m.endswith(".yml") else m
                for m in profile_content.get("modules", [])
            ]
            profile_module_names = {os.path.basename(m) for m in profile_modules}

            # existing: pre-select modules that come from the profile
            modules_without_parentdir = [os.path.basename(m) for m in self.modules]
            selected_modules = [m for m in profile_modules if m in modules_without_parentdir]

            # tailor the choices for add / remove -------------------------------
            add_candidates = [
                m for m in self.modules_w_parentdir
                if os.path.basename(m) not in profile_module_names
            ]
            remove_candidates = [
                m for m in self.modules_w_parentdir
                if os.path.basename(m) in profile_module_names
            ]

            module_add = st.multiselect(
                "Add Modules",
                add_candidates,
                help="Only modules that are not already listed in the selected profile."
            )
            module_remove = st.multiselect(
                "Remove Modules",
                remove_candidates,
                help="Only modules that are currently listed in the selected profile."
            )
        else:
            if not use_table_view:
                selected_modules_w_parentdir = st.multiselect(
                    "Modules", self.modules_w_parentdir,
                    help="Select specific modules to be exclusively used (classic view)."
                )
                selected_modules = [os.path.basename(m) for m in selected_modules_w_parentdir]
            else:
                # Build rows for the table view
                module_rows = []
                for mod in self.modules_w_parentdir:
                    full_path = os.path.join(self.MODULES_DIR, mod)
                    try:
                        content = FileManager.load_yaml_file(full_path)
                        module_rows.append({
                            "module_path": mod,  # show full relative path
                            "module": os.path.basename(mod),
                            "description": content.get("description", ""),
                            "processor_type": ", ".join(content.get("processor_type", []))
                            if isinstance(content.get("processor_type"), list)
                            else str(content.get("processor_type")),
                        })
                    except Exception as e:
                        module_rows.append({
                            "module_path": mod,
                            "module": os.path.basename(mod),
                            "description": f"Error: {e}",
                            "processor_type": "",
                        })

                df = pd.DataFrame(module_rows)

                # Render the table and read selection from session_state
                st.dataframe(
                    df[["module_path", "module", "description", "processor_type"]],
                    width='stretch',
                    hide_index=True,
                    selection_mode="multi-row",    # select many modules to run
                    on_select="rerun",
                    key="modules_table"
                )

                state = st.session_state.get("modules_table", {})
                rows = state.get("selection", {}).get("rows", []) if isinstance(state, dict) else []
                selected_modules = [df.iloc[i]["module"] for i in rows] if rows else []

        # Edit exactly one module at a time (no long scrolls)
        if selected_modules:
            with st.expander("Edit module configuration (optional)", expanded=False):
                module_choices = [os.path.basename(m) for m in selected_modules]
                module_to_edit = st.selectbox(
                    "Module to edit",
                    module_choices,
                    help="Pick one module, edit it, then pick the next."
                )
                if module_to_edit:
                    self.display_module_editors([module_to_edit])

        selected_case = st.selectbox("Case", self.cases, help="Select a case directory.")
        if not self.cases:
            st.warning("No cases found in /OSIR/share/cases/.")

        reprocess_case = st.checkbox(
            "Reprocess files of the case that were processed previously.",
            help="Check to reprocess files of the selected case that were processed earlier."
        )

        if st.button("Submit"):
            logger.debug("Module ADD" + str(module_add))
            self.process_submission(
                selected_profile,
                selected_modules,
                module_add,
                module_remove,
                selected_case,
                reprocess_case
            )

    def helper_tab(self):
        """
        Auxiliary tab to quickly view the content of profiles and modules.
        Helpful for understanding what's configured without leaving the UI.
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

    # TODO : Rewrite this
    # def _apply_overrides_to_monitor_case(self, monitor_case):
    #     """
    #     Apply in-memory YAML overrides (self.edited_modules) to each live module instance.
    #     This does NOT touch files on disk; it only mutates the in-memory objects that
    #     MonitorCase will use during this run.

    #     Args:
    #         monitor_case: a MonitorCase.MonitorCase instance with module_instances loaded.
    #     """
    #     if not getattr(self, "edited_modules", None):
    #         return

    #     for instance in getattr(monitor_case, "module_instances", []):
    #         # Try common attribute names to find the module file basename, e.g., "foo.yml"
    #         key = getattr(instance, "_filename", None) or getattr(instance, "filename", None)
    #         if not key:
    #             continue
    #         if key not in self.edited_modules:
    #             continue

    #         try:
    #             parsed = yaml.safe_load(self.edited_modules[key]) or {}
    #         except Exception as e:
    #             logger.error(f"[override] Invalid YAML for {key}: {e}")
    #             continue

    #         # Core swap-in of the parsed YAML
    #         try:
    #             # Keep this generous: many BaseModule fields are pulled from YAML
    #             instance.data            = parsed
    #             instance.version         = parsed.get("version")
    #             instance.author          = parsed.get("author")
    #             instance.description     = parsed.get("description")
    #             instance.type            = parsed.get("type")
    #             instance.os              = parsed.get("os")
    #             instance.requirements    = parsed.get("requirements", [])
    #             instance.processor_type  = parsed.get("processor_type", [])
    #             instance.processor_os    = parsed.get("processor_os", "Unknown processor os")
    #             instance.disk_only       = parsed.get("disk_only", False)
    #             instance.no_multithread  = parsed.get("no_multithread", False)
    #             instance.input           = BaseInput(parsed.get("input", {}))
    #             instance.output          = BaseOutput(parsed.get("output", {}))
    #             instance.env             = parsed.get("env", "")
    #             instance.optional        = parsed.get("optional", "")
    #             instance.endpoint        = parsed.get("endpoint", "")

    #             # If the module needs to (re)build a tool/runner from YAML
    #             if hasattr(instance, "init_tool"):
    #                 instance.init_tool()

    #             logger.debug(f"[override] Applied in-memory config to {key}")
    #         except Exception as e:
    #             logger.error(f"[override] Failed applying in-memory config to {key}: {e}")

    def process_submission_file(self, selected_module: list[str], selected_case: str, selected_file: str):
        """
        Launch processing for a specific file using a single selected module.

        Args:
            selected_module (list[str]): A list containing one module basename (e.g., ["foo.yml"]).
            selected_case (str): The selected case directory name.
            selected_file (str): The relative file path inside the case to process.

        Returns:
            None
        """
        case_path = os.path.join(self.CASES_DIR, selected_case)
        try:
            job = OsirProfileModel(modules=selected_module)
        except FileNotFoundError as e:
            st.error(f"Error creating ProcessorJob: {e}")
            logger.error(f"Error creating ProcessorJob: {e}")
            return

        modules_selected = job.modules

        # Used only for display: show module with its parent dir inside modules dir
        module_w_parentdir = FileManager.resolve_modules_parent_dir(modules_selected)
        modules_selected_str = "\n".join([f"- {module}" for module in module_w_parentdir])

        st.info(f"Modules selected:\n\n{modules_selected_str}")

        monitor_case = MonitorCase.MonitorCase(case_path, modules_selected, reprocess_case=True)

        # Apply in-memory YAML overrides BEFORE constraining input to a single file
        self._apply_overrides_to_monitor_case(monitor_case)

        # Limit processing to the single selected file for the (unique) module
        monitor_case.module_instances[0].input = OsirInput(type="file", name='^' + os.path.basename(selected_file) + '$')
        if monitor_case.module_instances[0].endpoint:
            monitor_case.module_instances[0].endpoint = ''

        # Run the setup in a background thread
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        executor.submit(monitor_case.setup_handler)

        st.success("Processing started.")
        st.page_link("pages/🏨_ProcessingStatus.py", label="Processing status", icon="🏨")

    def process_submission(self, selected_profile, selected_modules, module_add, module_remove, selected_case, reprocess_case):
        """
        Process the input values and initiate the processing job.

        Args:
            selected_profile (str): The selected profile name.
            selected_modules (list[str]): A list of selected module basenames.
            module_add (list[str]): Modules to add (relative paths under configs/modules).
            module_remove (list[str]): Modules to remove (relative paths under configs/modules).
            selected_case (str): The selected case directory name.
            reprocess_case (bool): If True, reprocess all files even if previously processed.

        Returns:
            None
        """
        # Process the input values (normalize to basenames)
        modules_to_add = [os.path.basename(m) for m in (module_add or [])]
        modules_to_remove = [os.path.basename(m) for m in (module_remove or [])]

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

        if selected_profile:
            profile_instance = OsirProfileModel.from_yaml(FileManager.get_profile_path(selected_profile))
            logger.debug(f"Processing job with profile: {selected_profile}")
            profile_instance.remove_modules(modules_to_remove)
            profile_instance.add_modules(modules_to_add)
            logger.debug(f"Modules to add: {modules_to_add}")
            logger.debug(f"Modules to remove: {modules_to_remove}")
        else:
            logger.debug(f"Selected modules: {selected_modules}")
            profile_instance = OsirProfileModel(modules=selected_modules)

        logger.debug(f"Case path: {case_path}")
        try:
            job = profile_instance
        except FileNotFoundError as e:
            st.error(f"Error creating ProcessorJob: {e}")
            logger.error(f"Error creating ProcessorJob: {e}")
            return

        modules_selected = job.modules

        # Used only for display: show module with its parent dir inside modules dir
        module_w_parentdir = FileManager.resolve_modules_parent_dir(modules_selected)
        modules_selected_str = "\n".join([f"- {module}" for module in module_w_parentdir])

        st.info(f"Modules selected:\n\n{modules_selected_str}")

        monitor_case = MonitorCase(case_path, modules_selected, reprocess_case)

        # TODO : Fix in memory change
        # Apply in-memory YAML overrides to all module instances for this run
        # self._apply_overrides_to_monitor_case(monitor_case)

        # Run the setup in a background thread
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

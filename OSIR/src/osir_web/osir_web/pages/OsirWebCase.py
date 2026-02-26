import os
import yaml
import pandas as pd
import streamlit as st

from typing import List
from osir_lib.core.FileManager import FileManager
from osir_lib.core.model.OsirProfileModel import OsirProfileModel
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_lib.core.OsirAgentConfig import OsirAgentConfig

from osir_service.watchdog.MonitorCase import MonitorCase
from osir_web.pages.OsirWebHeader import OsirWebHeader

from code_editor import code_editor
from osir_lib.logger import AppLogger

logger = AppLogger().get_logger()

class OsirWebCase:

    @staticmethod
    def _init_session_state():
        """Initialize session state variables if they don't exist."""
        if "edited_modules" not in st.session_state:
            st.session_state["edited_modules"] = {}
        if 'modules_table' in st.session_state:
            del st.session_state['modules_table']

    @staticmethod
    def render():
        OsirWebHeader.render(
            title="OSIR - Profile & Modules",
            subtitle="Execute Profile & Modules on case")
        OsirWebCase._init_session_state()
        OsirWebCase.tab1_main()

    @staticmethod
    def tab1_main():
        all_modules = FileManager.all_modules(relative=True)
        all_profiles = FileManager.all_profiles()
        all_cases = FileManager.all_cases()

        selected_profile = st.selectbox("Profile", [""] + all_profiles, help="Select a profile.")
        use_table_view = st.toggle("🔁 Switch to table view for module selection", value=False)

        selected_modules = []
        module_add = module_remove = []
        profile_instance = None
        
        if selected_profile:

            profile_instance = OsirProfileModel.from_name(selected_profile)

            add_candidates = [x for x in all_modules if os.path.basename(x) not in profile_instance.modules]

            module_add = st.multiselect(
                "Add Modules",
                add_candidates,
                help="Only modules that are not already listed in the selected profile."
            )
            module_remove = st.multiselect(
                "Remove Modules",
                profile_instance.modules,
                help="Only modules that are currently listed in the selected profile."
            )
        else:
            if not use_table_view:
                selected_modules_w_parentdir = st.multiselect(
                    "Modules", all_modules,
                    help="Select specific modules to be exclusively used (classic view)."
                )
                selected_modules = [os.path.basename(m) for m in selected_modules_w_parentdir]
            else:
                def on_table_select():
                    state = st.session_state.get("modules_table", {})
                    logger.info(state)
                    rows = state.get("selection", {}).get("rows", [])
                    if rows:  # only update when selection is non-empty
                        st.session_state["selected_module_rows"] = rows

                # Build rows for the table view
                module_rows = []
                for mod in all_modules:
                    try:
                        module = OsirModuleModel.from_name(mod)
                        module_rows.append({
                            "module_path": mod,
                            "module": module.filename,
                            "description": module.description,
                            "processor_type": ", ".join(module.processor_type)
                        })
                    except Exception as e:
                        module_rows.append({
                            "module_path": mod,
                            "module": module.filename,
                            "description": f"Error: {e}",
                            "processor_type": "",
                        })

                df = pd.DataFrame(module_rows)

                st.dataframe(
                    df[["module_path", "module", "description", "processor_type"]],
                    width='stretch',
                    hide_index=True,
                    selection_mode="multi-row",
                    on_select=on_table_select,
                    key="modules_table"
                )
                selected_rows = st.session_state.get("selected_module_rows", [])
                selected_modules = [df.iloc[i]["module"] for i in selected_rows]
        if selected_modules:
            with st.expander("Edit module configuration (optional)", expanded=False):
                module_choices = [os.path.basename(m) for m in selected_modules]
                module_to_edit = st.selectbox(
                    "Module to edit",
                    module_choices,
                    help="Pick one module, edit it, then pick the next."
                )
                if module_to_edit:
                    OsirWebCase.tab1_module_editor([module_to_edit])

        selected_case = st.selectbox("Case", all_cases, help="Select a case directory.")

        if not all_cases:
            st.warning("No cases found in /OSIR/share/cases/.")

        reprocess_case = st.checkbox(
            "Reprocess files of the case that were processed previously.",
            help="Check to reprocess files of the selected case that were processed earlier."
        )

        if st.button("Submit"):
            logger.debug("Module ADD" + str(module_add))
            OsirWebCase.process_submission(
                profile_instance,
                selected_modules,
                module_add,
                module_remove,
                selected_case,
                reprocess_case
            )

    @staticmethod
    def tab1_module_editor(selected_modules: list[str]):
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
            try:
                module_instance = OsirModuleModel.from_name(module_name)
                original = yaml.safe_dump(module_instance.model_dump(mode='json'), sort_keys=False)
            except Exception as e:
                original = f"# Error loading YAML for {module_name}: {e}"

            # Per-module editor buffer in session state
            state_key = f"mod_yaml__{module_name}"
            if state_key not in st.session_state:
                st.session_state[state_key] = original

            css_string = '''
                background-color: #bee1e5;

                body > #root .ace-streamlit-dark~& {
                background-color: #262830;
                }

                .ace-streamlit-dark~& span {
                color: #fff;
                opacity: 0.6;
                }

                span {
                color: #000;
                opacity: 0.5;
                }

                .code_editor-info.message {
                width: inherit;
                margin-right: 75px;
                order: 2;
                text-align: center;
                opacity: 0;
                transition: opacity 0.7s ease-out;
                }

                .code_editor-info.message.show {
                opacity: 0.6;
                }

                .ace-streamlit-dark~& .code_editor-info.message.show {
                opacity: 0.5;
                }
                '''

            info_bar = {
            "name": "language info",
            "css": css_string,
            "style": {
                        "order": "1",
                        "display": "flex",
                        "flexDirection": "row",
                        "alignItems": "center",
                        "width": "100%",
                        "height": "2.5rem",
                        "padding": "0rem 0.75rem",
                        "borderRadius": "8px 8px 8px 8px",
                        "zIndex": "9993",
                        "marginBottom": "10px"
                    },
            "info": [{
                        "name": f"✏️ Edit configuration for `{module_name}`",
                        "style": {"width": "500px"}
                    }]
            }
            custom_btns = [
                {
                "name": "Save",
                "feather": "Save",
                "hasText": True,
                "alwaysOn": True,
                "commands": ["save-state", ["response","saved"], ["infoMessage", {
                "text": "✅ Configuration Changed !",
                "timeout": 3000,
                "classToggle": "show"
            }]],
                "response": "saved",
                "style": {"right": "0.4rem"}
                },
                ]

            result = code_editor(
                st.session_state[state_key],
                lang="yaml",
                height=[20, 36],   # min/max visible line counts
                theme="vs-dark",
                key=f"code_editor__{module_name}",
                buttons=custom_btns,
                info=info_bar
            )

            new_text = result.get("text") if isinstance(result, dict) else None

            # Commit only meaningful updates (avoid accidental wipe when editor emits "")
            if new_text is not None:
                if new_text != st.session_state[state_key] and not (new_text == "" and st.session_state[state_key] != ""):
                    st.session_state[state_key] = new_text
                    st.session_state["edited_modules"][module_name] = new_text

            
            if result and result.get("type") == "saved":
                code_content = result.get("text", "")
                
                # Live YAML validation of the current buffer
                try:
                    yaml.safe_load(st.session_state[state_key])
                    st.caption("✅ YAML valid")
                except Exception as e:
                    st.error(f"YAML error: {e}")

                st.session_state[state_key] = code_content

            st.divider()
    
    @staticmethod
    def process_submission(
        profile_instance: OsirProfileModel = None,
        selected_modules: List[str] = None,
        modules_to_add: List[str] = [],
        modules_to_remove: List[str] = [],
        selected_case: str = None,
        reprocess_case: bool = False):
        # Validate inputs similar to the original argparse checks
        if not profile_instance and not selected_modules:
            st.error("At least one of profile or module must be specified.")
            return

        if (modules_to_add or modules_to_remove) and not profile_instance:
            st.error("module_add or module_remove can only be used when a profile is specified.")
            return

        if (profile_instance or selected_modules) and not selected_case:
            st.error("case must be set when using profile or module.")
            return
        
        case_path = FileManager.get_cases_path(selected_case)
        if not case_path:
            st.error(f"You selected a case that does not exist. Verify that {case_path} is the right path to process")
            return
        
        if profile_instance:
            logger.debug(f"Processing job with profile: {profile_instance.filename}")
            profile_instance.remove_modules(modules_to_remove)
            profile_instance.add_modules(modules_to_add)
            logger.debug(f"Modules to add: {modules_to_add}")
            logger.debug(f"Modules to remove: {modules_to_remove}")
        else:
            logger.debug(f"Selected modules: {selected_modules}")
            profile_instance = OsirProfileModel(modules=selected_modules)

        logger.debug(f"Case path: {case_path}")
     
        monitor_case = MonitorCase(case_path, profile_instance.modules, reprocess_case)

        if OsirWebCase._override_module_instances(monitor_case):
            monitor_case.start()

            st.info(f"Modules selected:\n\n{"\n".join([f"- {module._rel_path}" for module in monitor_case.module_instances])}")
            st.success("Processing started.")
            agent_config = OsirAgentConfig()

            st.page_link(f"http://{agent_config.master_host}:8501/OsirWebFlower", label="You can follow the status of your task in Status !", icon="📡")
    
    @staticmethod
    def _override_module_instances(monitor_case: MonitorCase):
        """
        Apply in-memory YAML overrides (edited_modules) to each live module instance.
        This does NOT touch files on disk; it only mutates the in-memory objects that
        MonitorCase will use during this run.
        Args:
            monitor_case: a MonitorCase.MonitorCase instance with module_instances loaded.
        """
        if not getattr(st.session_state, "edited_modules", None):
            return True
        
        module_instances = getattr(monitor_case, "module_instances", [])
        
        for i, instance in enumerate(module_instances):
            key = getattr(instance, "filename", None)
            if not key:
                continue
            if key not in st.session_state["edited_modules"]:
                continue
            try:
                parsed = yaml.safe_load(st.session_state["edited_modules"][key]) or {}
                modify_instance = OsirModuleModel(**parsed)
                # CORRECTION: Remplacer l'instance dans la liste
                monitor_case.module_instances[i] = modify_instance
                st.success("Modified !")

            except Exception as e:
                st.error(f"[Override] Invalid YAML for {key}: {e}")
                return False    

        return True
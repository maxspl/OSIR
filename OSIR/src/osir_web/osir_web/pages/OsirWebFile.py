import json
import os
import re
import streamlit as st
import time
from pathlib import Path
import streamlit.components.v1 as components
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.logger.logger import AppLogger
from osir_lib.core.FileManager import FileManager
from osir_lib.core.model.OsirModuleModel import OsirModuleModel

from osir_service.postgres.OsirDb import OsirDb
from osir_service.orchestration.TaskService import TaskService
from osir_web.pages.OsirWebUtils import OsirWebUtils

from osir_web.pages.OsirWebHeader import OsirWebHeader

logger = AppLogger().get_logger()


class OsirWebFile:

    @staticmethod
    def _init_session_state():
        """Initialize session state variables if they don't exist."""
        if 'last_selected_path' not in st.session_state:
            st.session_state.last_selected_path = ''
        if 'initial_selection' not in st.session_state:
            st.session_state.initial_selection = str(OSIR_PATHS.CASES_DIR)
        if 'previous_select' not in st.session_state:
            st.session_state.previous_select = ''
        if 'task_log' not in st.session_state:
            st.session_state.task_log = []
        if 'file_content' not in st.session_state:
            st.session_state.file_content = {}

    @staticmethod
    def render():
        OsirWebHeader.render(
            title="OSIR — File & Folder",
            subtitle="Execute modules on file or folder."
        )
        
        OsirWebFile._init_session_state()

        is_light = "false"
        if st.context.theme.type == 'light':
            is_light = "true"

        file_explorer_component = OsirWebFile.create_file_explorer_component(is_light=is_light)

        event = file_explorer_component(
            height=720,
            log=st.session_state.task_log,
            initial_selection=st.session_state.initial_selection,
            content=st.session_state.file_content
        )

        if event:
            logger.info(event)
            selected_path = event['path']
            if not selected_path:
                st.error("Path must be set in event try reload the page")
            match event['event']:
                case "LOAD_LOG":
                    if st.session_state.previous_select != selected_path:
                        st.session_state.task_log = OsirWebFile.get_taks_log(selected_path)
                        st.session_state.previous_select = selected_path
                        st.session_state.initial_selection = selected_path
                        st.rerun()
                case "RUN_MODULE":
                    try:
                        module_model = OsirModuleModel.from_yaml(OSIR_PATHS.MODULES_DIR / event['action_id'])
                        module_model.input.match = selected_path
                        case_path = re.match(r'^(.*?/cases/[^/]+)', selected_path).group(1)
                        with OsirDb() as db:
                            case_uuid = db.case.get(name=os.path.basename(case_path)).case_uuid
                        TaskService.push_task(case_path=case_path, module_instance=module_model, case_uuid=case_uuid)
                        OsirWebUtils.toast(
                            txt="Task started ! Follow the progression in 'Task On Going' or in 'Orchestration Monitoring'",
                            background="#28a745",
                            icon="🎉")
                    except Exception as e:
                        OsirWebUtils.toast(
                            txt="An error occured report it in 'Report & Github'",
                            background="#dc2626",
                            icon="🚨")
                        logger.error_handler(e)
                case "RUN_FOLDER_ACTION":
                    try:
                        module_model = OsirModuleModel.from_yaml(OSIR_PATHS.MODULES_DIR / event['action_id'])
                        case_path = re.match(r'^(.*?/cases/[^/]+)', selected_path).group(1)
                        with OsirDb() as db:
                            case_uuid = db.case.get(name=os.path.basename(case_path)).case_uuid
                        if os.path.isdir(selected_path):
                            files = [os.path.join(selected_path, f) for f in os.listdir(selected_path) if os.path.isfile(os.path.join(selected_path, f))]
                            if not files:
                                raise ValueError(f"No files found in directory: {selected_path}")
                            for file in files:
                                logger.info(f"Processing file: {file}")
                                module_model.input.match = file
                                TaskService.push_task(case_path=case_path, module_instance=module_model, case_uuid=case_uuid)

                            OsirWebUtils.toast(
                                txt=f"Tasks started for {len(files)} files! Follow progression in 'Task On Going' or 'Orchestration Monitoring'",
                                background="#28a745",
                                icon="🎉"
                            )
                        else:
                            raise ValueError(f"Selected path is not a directory: {selected_path}")

                    except Exception as e:
                        OsirWebUtils.toast(
                            txt="An error occurred. Report it in 'Report & Github'",
                            background="#dc2626",
                            icon="🚨"
                        )
                        logger.error_handler(e)
                case "LOAD_CONTENT":
                    path = event["path"]
                    try:
                        # Resolve real absolute path (resolves ../ etc)
                        resolved = Path(path).resolve()
                        allowed = Path("/OSIR/share/cases").resolve()

                        # Security checks
                        if not resolved.is_relative_to(allowed):
                            raise PermissionError("Access denied: path outside allowed directory")
                        if not resolved.exists():
                            raise FileNotFoundError("File not found")
                        if not resolved.is_file():
                            raise ValueError("Path is not a file")
                        if resolved.stat().st_size == 0:
                            raise ValueError("File is empty")
                        
                        logger.info(resolved)
                        with open(resolved, "r", encoding="utf-8", errors="replace") as f:
                            lines = []
                            for _ in range(5):
                                line = f.readline()
                                if not line:
                                    break
                                lines.append(line)
                        content = "".join(lines)

                    except PermissionError as e:
                        content = f"⛔ {e}"
                    except FileNotFoundError as e:
                        content = f"❓ {e}"
                    except ValueError as e:
                        content = f"⚠️ {e}"
                    except Exception as e:
                        content = f"❌ Error reading file: {e}"

                    st.session_state.previous_select = path
                    st.session_state.initial_selection = path
                    st.session_state.file_content = {path: content}
                    st.rerun()
                case "DOWNLOAD":
                    path = event["path"]
                    try:
                        resolved = Path(path).resolve()
                        allowed = Path("/OSIR/share/cases").resolve()

                        if not resolved.is_relative_to(allowed):
                            raise PermissionError("Access denied")
                        if not resolved.exists() or not resolved.is_file():
                            raise FileNotFoundError("File not found")

                        st.divider()

                        with open(resolved, "rb") as f:
                            OsirWebUtils.toast(
                                txt="File successfuly loaded go at the bottom of the page.",
                                background="#28a745",
                                icon="🎉"
                            )
                            st.download_button(
                                label="⬇️ Your download is ready ! Click on me !",
                                data=f,
                                file_name=resolved.name,
                                mime="application/octet-stream",
                                key=f"dl_{resolved.name}_{int(time.time())}"
                            )

                    except Exception as e:
                        st.error(f"❌ {e}")

    @staticmethod
    def get_taks_log(path: str):
        with OsirDb() as db:
            logs = db.task.get_by_output(path)
            if logs:
                return [{**log, "path": path} for log in logs.get_logs()]    
            return [{'msg': "There is no log associated with this file", "level": "info", "ts": "", "path": path}]

    @staticmethod
    def get_all_module(for_file: bool = True):
        module_rows = []
        modules = FileManager.get_yaml_files(OSIR_PATHS.MODULES_DIR, relative=True)
        for mod in modules:
            full_path = os.path.join(OSIR_PATHS.MODULES_DIR, mod)
            try:
                content = OsirModuleModel.from_yaml(full_path)
                if for_file and content.input.type == 'file':
                    module_rows.append({
                        "id": mod,
                        "label": mod,
                        "description": content.description
                    })
                if not for_file and content.input.type == 'dir':
                    module_rows.append({
                        "id": mod,
                        "label": mod,
                        "description": content.description
                    })
            except Exception as e:
                logger.error_handler(e)

        return module_rows

    @staticmethod
    def file_explorer(
        root_path: str,
        max_depth: int = 7,
        height: int = 650,
        key: str = None,
        initial_selection: str = None,
        file_task_log: list = None,
        file_actions: list = None,
        folder_actions: list = None,
        light_mode: str = 'true'
    ):
        """
        Renders an interactive file explorer iframe.

        Returns a dict with event info when a file/folder is selected OR when
        an action is triggered:

            Selection event:
            {
                "event": "SELECT|FILE" | "SELECT|DIR",
                "path": "/full/path/to/item",
                "name": "item_name",
                "is_dir": True/False,
                "size": int (bytes, 0 for dirs)
            }

            Action event:
            {
                "event": "ACTION",
                "action_id": "module_id",
                "path": "/full/path/to/item",
                "name": "item_name",
                "is_dir": True/False,
            }
        """
        tree = OsirWebFile._build_tree(root_path, max_depth=max_depth)
        tree_json = json.dumps(tree)
        root_json = json.dumps(root_path)
        initial_selection_json = json.dumps(initial_selection)
        file_task_log_json = json.dumps(file_task_log or [])
        file_actions_json = json.dumps(file_actions or [])
        folder_actions_json = json.dumps(folder_actions or [])
        light_mode = light_mode
        html = f"""<!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8"/>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
            <style>
            :root {{
                --bg-dark: #0d0f14;
                --bg-darker: #0d1117;
                --bg-panel: #161b22;
                --bg-item-hover: #1f2937;
                --bg-selected: #21c55d18;
                --bg-border: #21262d;
                --bg-scrollbar: #30363d;
                --text-primary: #c9d1d9;
                --text-secondary: #6e7681;
                --text-highlight: #21c55d;
                --text-warn: #f0a43a;
                --text-error: #f85149;
                --text-info: #58a6ff;
                --border-radius: 10px;
                --card-border-radius: 12px;
                --font-main: "Source Sans", sans-serif;
                --font-mono: 'JetBrains Mono', monospace;
                --font-title: "Source Sans", sans-serif;
            }}
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}

            html, body {{
                background: transparent;
                color: var(--text-primary);
                font-family: var(--font-main);
                font-size: 13px;
                height: 100%;
                overflow: hidden;
            }}

            .card-container {{
                background: var(--bg-darker);
                border: 1px solid var(--bg-border);
                border-radius: var(--card-border-radius);
                height: 100%;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }}

            .layout {{
                display: flex;
                flex-direction: column;
                height: 100%;
            }}

            /* ── Toolbar ── */
            .toolbar {{
                height: 50px;
                border-bottom: 1px solid var(--bg-border);
                padding: 8px 12px;
                display: flex;
                align-items: center;
                gap: 8px;
                flex-shrink: 0;
                background: var(--bg-darker);
                border-top-left-radius: var(--card-border-radius);
                border-top-right-radius: var(--card-border-radius);
            }}
            .toolbar input {{
            height: 30px;
                flex: 1;
                background: var(--bg-dark);
                border: 1px solid var(--bg-border);
                border-radius: var(--border-radius);
                padding: 5px 10px;
                color: var(--text-primary);
                font-size: 12px;
                outline: none;
                transition: border-color 0.2s;
            }}
            .toolbar input:focus {{ border-color: var(--text-highlight); }}

            .btn {{
                background: #21c55d15;
                border: 1px solid #21c55d33;
                border-radius: 5px;
                color: var(--text-highlight);
                padding: 5px 10px;
                cursor: pointer;
                font-size: 11px;
                transition: background 0.15s;
                white-space: nowrap;
            }}
            .btn:hover {{ background: #21c55d25; }}

            /* ── Main split ── */
            .main {{
                display: flex;
                flex: 1;
                overflow: hidden;
                background: var(--bg-dark);
            }}

            /* ── Tree panel ── */
            .tree-panel {{
                width: 280px;
                background: var(--bg-darker);
                border-right: 1px solid var(--bg-border);
                overflow-y: auto;
                flex-shrink: 0;
                padding: 6px 0;
            }}
            .tree-panel::-webkit-scrollbar {{ width: 5px; }}
            .tree-panel::-webkit-scrollbar-track {{ background: var(--bg-darker); }}
            .tree-panel::-webkit-scrollbar-thumb {{ background: var(--bg-scrollbar); border-radius: 3px; }}

            /* ── Tree items ── */
            .tree-item {{
                display: flex;
                align-items: center;
                gap: 5px;
                padding: 4px 8px;
                cursor: pointer;
                border-radius: 4px;
                margin: 1px 4px;
                transition: background 0.12s;
                white-space: nowrap;
                overflow: hidden;
                user-select: none;
            }}
            .tree-item:hover {{ background: var(--bg-item-hover); }}
            .tree-item.selected {{
                background: var(--bg-selected);
                outline: 1px solid #21c55d33;
            }}
            .toggle {{ width: 12px; text-align: center; color: var(--text-secondary); font-size: 9px; flex-shrink: 0; transition: transform 0.15s; }}
            .file-icon {{ font-size: 13px; flex-shrink: 0; }}
            .file-name {{ overflow: hidden; text-overflow: ellipsis; font-size: 12px; color: var(--text-primary); }}
            .tree-item.is-dir .file-name {{ font-weight: 600; }}
            .children {{ display: none; padding-left: 14px; }}
            .children.open {{ display: block; }}

            /* ── Detail panel ── */
            .detail-panel {{
                flex: 1;
                overflow-y: auto;
                padding: 18px 20px;
                background: var(--bg-dark);
                display: flex;
                flex-direction: column;
                gap: 16px;
            }}
            .detail-panel::-webkit-scrollbar {{ width: 5px; }}
            .detail-panel::-webkit-scrollbar-track {{ background: var(--bg-dark); }}
            .detail-panel::-webkit-scrollbar-thumb {{ background: var(--bg-scrollbar); border-radius: 3px; }}

            .empty-state {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                color: var(--text-secondary);
                gap: 10px;
                font-family: var(--font-title);
            }}
            .empty-state .big {{ font-size: 40px; }}

            .detail-title {{
                font-family: var(--font-title);
                font-size: 18px;
                font-weight: 700;
                color: var(--text-primary);
                margin-bottom: 4px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .detail-subtitle {{
                font-size: 11px;
                color: var(--text-secondary);
                font-family: var(--font-mono);
                word-break: break-all;
            }}

            .stats {{
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
            }}
            .stat {{
                background: var(--bg-panel);
                border: 1px solid var(--bg-border);
                border-radius: 7px;
                padding: 10px 14px;
                min-width: 120px;
            }}
            .stat .slabel {{ font-size: 10px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 3px; }}
            .stat .sval {{ font-size: 13px; color: var(--text-highlight); font-weight: 600; }}

            /* ── Folder contents list ── */
            .children-list {{
                overflow-y: auto;
                overscroll-behavior: contain;
                background: var(--bg-panel);
                border: 1px solid var(--bg-border);
                border-radius: 8px;
            }}
            .cl-header {{
                padding: 8px 14px;
                border-bottom: 1px solid var(--bg-border);
                font-size: 11px;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 0.1em;
            }}
            .cl-row {{
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 7px 14px;
                border-bottom: 1px solid #21262d1a;
                cursor: pointer;
                transition: background 0.12s;
                font-size: 12px;
            }}
            .cl-row:last-child {{ border-bottom: none; }}
            .cl-row:hover {{ background: var(--bg-item-hover); }}
            .cl-row .ci {{ width: 18px; text-align: center; }}
            .cl-row .cn {{ flex: 1; color: var(--text-primary); }}
            .cl-row .cn.d {{ font-weight: 600; }}
            .cl-row .cs {{ color: var(--text-secondary); font-size: 11px; }}

            /* ── Shared card header ── */
            .card-header {{
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 9px 14px;
                border-bottom: 1px solid var(--bg-border);
                font-size: 11px;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 0.1em;
                font-weight: 600;
            }}
            .card-header .card-icon {{ font-size: 13px; }}
            .card-header .badge {{
                margin-left: auto;
                background: #21c55d22;
                color: var(--text-highlight);
                font-size: 10px;
                padding: 2px 7px;
                border-radius: 99px;
                border: 1px solid #21c55d33;
                font-family: var(--font-mono);
            }}

            /* ── Task Log Card ── */
            .task-log-card {{
                background: var(--bg-panel);
                border: 1px solid var(--bg-border);
                border-radius: 8px;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }}

            .log-body {{
                overflow-y: auto;
                overscroll-behavior: contain;
            }}
            .log-body::-webkit-scrollbar {{ width: 4px; }}
            .log-body::-webkit-scrollbar-track {{ background: var(--bg-panel); }}
            .log-body::-webkit-scrollbar-thumb {{ background: var(--bg-scrollbar); border-radius: 3px; }}

            /* entry whose path doesn't match the selected file */
            .log-entry.dimmed {{
                opacity: 0.32;
                filter: grayscale(0.4);
            }}

            .log-entry {{
                display: flex;
                align-items: flex-start;
                gap: 10px;
                padding: 7px 14px;
                border-bottom: 1px solid #21262d22;
                font-family: var(--font-mono);
                font-size: 11px;
                transition: background 0.1s;
            }}
            .log-entry:last-child {{ border-bottom: none; }}
            .log-entry:hover {{ background: var(--bg-item-hover); }}

            .log-ts {{
                color: var(--text-secondary);
                white-space: nowrap;
                flex-shrink: 0;
                font-size: 10px;
                padding-top: 2px;
            }}
            .log-level {{
                font-size: 10px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                padding: 1px 6px;
                border-radius: 4px;
                flex-shrink: 0;
            }}
            .log-level.info    {{ background: #58a6ff18; color: var(--text-info);      border: 1px solid #58a6ff33; }}
            .log-level.warn    {{ background: #f0a43a18; color: var(--text-warn);      border: 1px solid #f0a43a33; }}
            .log-level.error   {{ background: #f8514918; color: var(--text-error);     border: 1px solid #f8514933; }}
            .log-level.success {{ background: #21c55d18; color: var(--text-highlight); border: 1px solid #21c55d33; }}
            .log-level.debug   {{ background: #a371f718; color: var(--text-muted);      border: 1px solid #a371f733; }}
            .log-msg {{ color: var(--text-primary); flex: 1; line-height: 1.5; word-break: break-all; }}

            /* small chip showing which file a log entry belongs to */
            .log-path-chip {{
                font-size: 10px;
                font-family: var(--font-mono);
                background: #58a6ff12;
                color: #58a6ff99;
                border: 1px solid #58a6ff22;
                border-radius: 4px;
                padding: 1px 5px;
                white-space: nowrap;
                flex-shrink: 0;
                max-width: 120px;
                overflow: hidden;
                text-overflow: ellipsis;
            }}

            .log-empty {{
                padding: 16px 14px;
                color: var(--text-secondary);
                font-size: 12px;
                font-style: italic;
                text-align: center;
            }}

            /* ── Action Card ── */
            .action-cards-wrapper {{
                display: flex;
                flex-direction: row;
                align-items: stretch;
                gap: 10px;
                margin-top: auto;
            }}

            .action-card {{
                background: var(--bg-panel);
                border: 1px solid var(--bg-border);
                border-radius: 8px;
                overflow: visible;
                flex: 1;
            }}

            .folder-action-card {{
                flex: 1;
            }}

            .action-body {{
                padding: 12px 14px;
                display: flex;
                align-items: center;
                gap: 10px;
                flex-wrap: wrap;
            }}

            .action-select {{
                flex: 1;
                min-width: 160px;
                background: var(--bg-dark);
                border: 1px solid var(--bg-border);
                border-radius: 6px;
                padding: 7px 28px 7px 10px;
                color: var(--text-primary);
                font-size: 12px;
                font-family: var(--font-main);
                outline: none;
                cursor: pointer;
                transition: border-color 0.2s;
                appearance: none;
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%236e7681'/%3E%3C/svg%3E");
                background-repeat: no-repeat;
                background-position: right 10px center;
            }}
            .action-select:focus {{ border-color: var(--text-highlight); }}
            .action-select option {{ background: var(--bg-panel); color: var(--text-primary); }}

            .action-desc {{
                width: 100%;
                font-size: 11px;
                color: var(--text-secondary);
                padding: 0 2px 4px 2px;
                min-height: 16px;
                font-style: italic;
            }}

            .run-btn {{
                background: linear-gradient(135deg, #21c55d22, #21c55d15);
                border: 1px solid #21c55d55;
                border-radius: 6px;
                color: var(--text-highlight);
                padding: 7px 16px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 600;
                font-family: var(--font-main);
                transition: background 0.15s, transform 0.1s, box-shadow 0.15s;
                display: flex;
                align-items: center;
                gap: 6px;
                white-space: nowrap;
            }}
            .run-btn:hover {{
                background: linear-gradient(135deg, #21c55d33, #21c55d22);
                box-shadow: 0 0 12px #21c55d22;
            }}
            .run-btn:active {{ transform: scale(0.97); }}
            .run-btn .run-icon {{ font-size: 13px; }}

            /* ── Status bar ── */
            .status-bar {{
                background: var(--bg-panel);
                border-top: 1px solid var(--bg-border);
                padding: 4px 14px;
                font-size: 11px;
                color: var(--text-secondary);
                display: flex;
                gap: 20px;
                flex-shrink: 0;
                border-bottom-left-radius: var(--card-border-radius);
                border-bottom-right-radius: var(--card-border-radius);
            }}
            .status-bar .highlight {{ color: var(--text-highlight); }}

            /* ── Event flash ── */
            .event-flash {{
                position: fixed;
                bottom: 30px;
                right: 16px;
                background: var(--text-highlight);
                color: var(--bg-dark);
                font-size: 11px;
                font-weight: 600;
                padding: 6px 12px;
                border-radius: var(--border-radius);
                opacity: 0;
                transform: translateY(8px);
                transition: opacity 0.2s, transform 0.2s;
                pointer-events: none;
                z-index: 999;
            }}
            .event-flash.show {{ opacity: 1; transform: translateY(0); }}

            /* ── Light mode ── */
            .light-mode {{
                --bg-dark: #f6f8fa;
                --bg-darker: #ffffff;
                --bg-panel: #f6f8fa;
                --bg-item-hover: #eaeef2;
                --bg-selected: #d8f5e2;
                --bg-border: #d0d7de;
                --bg-scrollbar: #d0d7de;
                --text-primary: #31333F;
                --text-secondary: #57606a;
                --text-highlight: #1a7f37;
            }}
            .light-mode .action-select {{
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%2357606a'/%3E%3C/svg%3E");
            }}
            .content-card {{
                background: var(--bg-panel);
                border: 1px solid var(--bg-border);
                border-radius: 8px;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }}

            .content-body {{
                padding: 12px 14px;
                font-family: var(--font-mono);
                font-size: 11px;
                color: var(--text-primary);
                white-space: pre-wrap;
                word-break: break-all;
                overflow-y: auto;
                max-height: 300px;
                line-height: 1.6;
            }}

            .content-body::-webkit-scrollbar {{ width: 4px; }}
            .content-body::-webkit-scrollbar-track {{ background: var(--bg-panel); }}
            .content-body::-webkit-scrollbar-thumb {{ background: var(--bg-scrollbar); border-radius: 3px; }}

            .content-empty {{
                padding: 16px 14px;
                color: var(--text-secondary);
                font-size: 12px;
                font-style: italic;
                text-align: center;
            }}
            </style>
            </head>
            <body>
            <div class="card-container">
            <div class="layout">
                <div class="toolbar">
                <input type="text" id="search" placeholder="🔍 Search..." oninput="filterTree(this.value)"/>
                <button class="btn" onclick="expandAll()">➕</button>
                <button class="btn" onclick="collapseAll()">➖</button>
                </div>

                <div class="main">
                <div class="tree-panel" id="treePanel"></div>
                <div class="detail-panel" id="detailPanel">
                    <div class="empty-state">
                    <span class="big">📁</span>
                    <span>Select an item</span>
                    </div>
                </div>
                </div>

                <div class="status-bar">
                <span id="statItems"></span>
                <span id="statSel">No selection</span>
                </div>
            </div>

            <div class="event-flash" id="flash"></div>
            </div>

            <script>
            // ── Data ──────────────────────────────────────────────────
            const TREE              = {tree_json};
            const ROOT              = {root_json};
            let INITIAL_SELECTION = {initial_selection_json};
            let FILE_CONTENT = {{}};
            let FILE_TASK_LOG     = {file_task_log_json};
            const FILE_ACTIONS      = {file_actions_json};
            const FOLDER_ACTIONS    = {folder_actions_json};
            localStorage.setItem('fileExplorerLightMode', '{light_mode}');
            let allNodes    = [];
            let isLightMode = false;
            let currentItem = null;   // tracks selected item for action dispatch

            // ── Utilities ─────────────────────────────────────────────
            function getIcon(name, isDir) {{
            if (isDir) return '📁';
            const ext = name.split('.').pop().toLowerCase();
            return ({{
                py:'🐍',js:'📜',ts:'📘',jsx:'⚛️',tsx:'⚛️',
                html:'🌐',css:'🎨',scss:'🎨',
                json:'📋',xml:'📋',
                md:'📝',txt:'📄',csv:'📊',
                pdf:'📕',
                png:'🖼️',jpg:'🖼️',jpeg:'🖼️',gif:'🖼️',svg:'🎨',webp:'🖼️',
                mp4:'🎬',mov:'🎬',mp3:'🎵',wav:'🎵',
                zip:'📦',tar:'📦',gz:'📦',rar:'📦',
                sh:'⚡',bash:'⚡',
                yml:'⚙️',yaml:'⚙️',toml:'⚙️',env:'🔒',ini:'⚙️',cfg:'⚙️',
                sql:'🗄️',db:'🗄️',sqlite:'🗄️',
                exe:'⚙️',dmg:'💿',deb:'📦',
                go:'🐹',rs:'🦀',cpp:'⚙️',c:'⚙️',java:'☕',rb:'💎',php:'🐘',
            }})[ext] || '📄';
            }}

            function fmtSize(b) {{
            if (!b) return '—';
            const u = ['B','KB','MB','GB'];
            let i = 0;
            while (b >= 1024 && i < 3) {{ b /= 1024; i++; }}
            return b.toFixed(1) + ' ' + u[i];
            }}

            function escHtml(s) {{
            return String(s)
                .replace(/&/g, '&amp;').replace(/</g, '&lt;')
                .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
            }}
            function escAttr(s) {{ return escHtml(s); }}


            // ── Streamlit events ──────────────────────────────────────
            function sendDataToPython(data) {{
            sendMessageToStreamlitClient("streamlit:setComponentValue", data);
            }}

            function sendMessageToStreamlitClient(type, data) {{
            var outData = Object.assign({{ isStreamlitMessage: true, type: type }}, data);
            window.parent.postMessage(outData, "*");
            }}

            function sendEvent(eventType, item) {{
            sendDataToPython({{
                value: {{
                action_id: 'SELECT',
                event:  eventType,
                path:   item.path,
                name:   item.name,
                is_dir: item.is_dir,
                size:   item.size || 0,
                }},
                dataType: "json",
            }});
            flashEvent(eventType, item.name);
            }}

            function sendActionEvent(actionId, item, event) {{
            const isString = typeof item === 'string';
            sendDataToPython({{
                value: {{
                event:     event,
                action_id: actionId,
                path:      isString ? item : item.path,
                name:      isString ? "" : item.name,
                is_dir:    isString ? false : item.is_dir,
                }},
                dataType: "json",
            }});
            flashEvent("RUN › " + actionId, isString ? item : item.name);
            }}

            function flashEvent(type, name) {{
            const el = document.getElementById('flash');
            el.textContent = `${{type.toUpperCase()}} → ${{name}}`;
            el.classList.add('show');
            clearTimeout(el._t);
            el._t = setTimeout(() => el.classList.remove('show'), 1800);
            }}

            function buildContentHTML(filePath) {{
                const entry = FILE_CONTENT[filePath];
                if (!entry) {{
                    return '<div class="content-empty">Not Loaded</div>';
                }}
                return `<div class="content-body">${{escHtml(entry)}}</div>`;
            }}
            // ── Task-Log HTML builder ─────────────────────────────────
            // selectedPath: the currently selected file's full path (or null)
            // Entries with a "path" field are highlighted only when path === selectedPath;
            // entries without a "path" field are always shown at full opacity.
            function buildTaskLogHTML(selectedPath) {{
            
            const filteredLogs = FILE_TASK_LOG.filter(entry => entry.path === selectedPath);
            if (!filteredLogs || filteredLogs.length === 0) {{
                return '<div class="log-empty">Not Loaded</div>';
            }}

            const rows = FILE_TASK_LOG.map(entry => {{
                if(entry.path == selectedPath){{
                const level   = (entry.level || 'info').toLowerCase();
                const ts      = entry.ts   || '';
                const msg     = entry.msg  || '';
                const logPath = entry.path || null;

                // Determine if this entry is "owned" by the selected file.
                // If the entry has no path → always fully visible.
                // If it has a path → dimmed when it doesn't match the selected file.
                const isPathMismatch = logPath !== null && logPath !== selectedPath;
                const dimClass = isPathMismatch ? ' dimmed' : '';

                return `<div class="log-entry${{dimClass}}">
                <span class="log-ts">${{escHtml(ts)}}</span>
                <span class="log-level ${{level}}">${{level}}</span>
                <span class="log-msg">${{escHtml(msg)}}</span>
                </div>`;
                }}
                
            }}).join('');

            return `<div class="log-body">${{rows}}</div>`;
            }}

            // ── Action Card HTML builder ──────────────────────────────
            function buildActionCardHTML(actions, selectId, descId) {{
                if (!actions || actions.length === 0) return '';

                const options = actions.map(a =>
                    `<option value="${{escAttr(a.id)}}" data-desc="${{escAttr(a.description || '')}}">${{escHtml(a.label || a.id)}}</option>`
                ).join('');

                const firstDesc = (actions[0] && actions[0].description) ? escHtml(actions[0].description) : '';
                const firstDescFile = (FILE_ACTIONS[0] && FILE_ACTIONS[0].description) ? escHtml(FILE_ACTIONS[0].description) : '';

                const folderSelectId = selectId + '_folder';
                const folderDescId   = descId   + '_folder';

                const fileOptions = FILE_ACTIONS.map(a =>
                    `<option value="${{escAttr(a.id)}}" data-desc="${{escAttr(a.description || '')}}">${{escHtml(a.label || a.id)}}</option>`
                ).join('');

                const folderActionCard = selectId === 'folderActionSel' ? `
                    <div class="action-card folder-action-card">
                        <div class="card-header">
                            <span class="card-icon">📁</span>
                            Action on all files in dir
                        </div>
                        <div class="action-body">
                            <select class="action-select" id="${{folderSelectId}}"
                                    onchange="updateActionDesc('${{folderSelectId}}','${{folderDescId}}')">
                                ${{fileOptions}}
                            </select>
                            <button class="run-btn" onclick="runFolderAction('${{folderSelectId}}')">
                                <span class="run-icon">▶</span> Run
                            </button>
                            <div class="action-desc" id="${{folderDescId}}">${{firstDescFile}}</div>
                        </div>
                    </div>` : '';

                return `
                <div class="action-cards-wrapper">
                    <div class="action-card">
                        <div class="card-header">
                            <span class="card-icon">⚡</span>
                            Action
                        </div>
                        <div class="action-body">
                            <select class="action-select" id="${{selectId}}"
                                    onchange="updateActionDesc('${{selectId}}','${{descId}}')">
                                ${{options}}
                            </select>
                            <button class="run-btn" onclick="runAction('${{selectId}}')">
                                <span class="run-icon">▶</span> Run
                            </button>
                            <div class="action-desc" id="${{descId}}">${{firstDesc}}</div>
                        </div>
                    </div>
                    ${{folderActionCard}}
                </div>`;
            }}

            function updateActionDesc(selectId, descId) {{
            const sel  = document.getElementById(selectId);
            const desc = document.getElementById(descId);
            if (sel && desc) {{
                const opt = sel.options[sel.selectedIndex];
                desc.textContent = opt ? (opt.dataset.desc || '') : '';
            }}
            }}

            function runAction(selectId) {{
            if (!currentItem) return;
            const sel = document.getElementById(selectId);
            if (!sel) return;
            const actionId = sel.value;
            if (actionId) sendActionEvent(actionId, currentItem, 'RUN_MODULE');
            }}
            function runFolderAction(selectId) {{
                if (!currentItem) return;
                const sel = document.getElementById(selectId);
                if (!sel) return;
                const actionId = sel.value;
                if (actionId) sendActionEvent(actionId, currentItem, 'RUN_FOLDER_ACTION');
            }}

            // ── Build tree DOM ────────────────────────────────────────
            function buildTree(items, container) {{
            items.forEach(item => {{
                const wrap = document.createElement('div');

                const row = document.createElement('div');
                row.className = 'tree-item' + (item.is_dir ? ' is-dir' : '');
                row.dataset.path = item.path;
                row.dataset.nameLower = item.name.toLowerCase();

                const toggle = document.createElement('span');
                toggle.className = 'toggle';
                toggle.textContent = item.is_dir && item.children.length ? '▶' : '';

                const icon = document.createElement('span');
                icon.className = 'file-icon';
                icon.textContent = getIcon(item.name, item.is_dir);

                const name = document.createElement('span');
                name.className = 'file-name';
                name.textContent = item.name;

                row.appendChild(toggle);
                row.appendChild(icon);
                row.appendChild(name);

                let childrenEl = null;
                if (item.is_dir && item.children.length) {{
                childrenEl = document.createElement('div');
                childrenEl.className = 'children';
                buildTree(item.children, childrenEl);
                }}

                row.addEventListener('click', e => {{
                e.stopPropagation();
                document.querySelectorAll('.tree-item.selected').forEach(el => el.classList.remove('selected'));
                row.classList.add('selected');

                if (item.is_dir && childrenEl) {{
                    const opening = !childrenEl.classList.contains('open');
                    childrenEl.classList.toggle('open', opening);
                    toggle.textContent = opening ? '▼' : '▶';
                    icon.textContent   = opening ? '📂' : '📁';     
                }} else {{
                }}

                showDetail(item);
                document.getElementById('statSel').innerHTML =
                    `<span class="highlight"></span> ${{item.path}}`;
                }});

                wrap.appendChild(row);
                if (childrenEl) wrap.appendChild(childrenEl);
                container.appendChild(wrap);
                allNodes.push({{ row, item }});
            }});
            }}

            // ── Detail panel ──────────────────────────────────────────
            function showDetail(item) {{
            currentItem = item;
            const p   = document.getElementById('detailPanel');
            const ext = (!item.is_dir && item.name.includes('.'))
                ? item.name.split('.').pop().toUpperCase() : '';

            const header = `
                <div>
                <div class="detail-title">
                    <span>${{getIcon(item.name, item.is_dir)}}</span>
                    ${{escHtml(item.name)}}
                </div>
                <div class="detail-subtitle">${{escHtml(item.path)}}</div>
                </div>`;

            if (item.is_dir) {{
                // ── Folder detail ──────────────────────────────────────
                const childRows = (item.children || []).map(c => `
                <div class="cl-row" onclick="focusNode('${{c.path}}')">
                    <span class="ci">${{getIcon(c.name, c.is_dir)}}</span>
                    <span class="cn ${{c.is_dir ? 'd' : ''}}">${{escHtml(c.name)}}</span>
                    <span class="cs">${{c.is_dir ? c.children.length + ' item(s)' : fmtSize(c.size)}}</span>
                </div>`).join('');

                const contentsCard = `
                <div class="children-list">
                    <div class="cl-header">Contents — ${{(item.children||[]).length}} item(s)</div>
                    ${{childRows || '<div style="padding:12px 14px;color:#6e7681;font-size:12px;">Empty folder</div>'}}
                </div>`;

                const folderActionCard = buildActionCardHTML(
                FOLDER_ACTIONS, 'folderActionSel', 'folderActionDesc'
                );

                

                p.innerHTML = `
                ${{header}}
                <div class="stats">
                    <div class="stat"><div class="slabel">Type</div><div class="sval">Folder</div></div>
                    <div class="stat"><div class="slabel">Items</div><div class="sval">${{(item.children||[]).length}}</div></div>
                </div>
                ${{contentsCard}}
                ${{folderActionCard}}
                `;

            }} else {{
                // ── File detail ────────────────────────────────────────
                // const matchedCount = FILE_TASK_LOG.filter(e => !e.path || e.path === item.path).length;
                const contentCard = `
                <div class="content-card">
                    <div class="card-header">
                        <span class="card-icon">📄</span>
                        Content
                        <div class="badge btn" onclick="sendActionEvent('LOAD_CONTENT', '${{item.path}}', 'LOAD_CONTENT')">Load content</div>
                    </div>
                    ${{buildContentHTML(item.path)}}
                </div>`;
                const taskLogCard = `
                <div class="task-log-card">
                    <div class="card-header">
                    <span class="card-icon">📋</span>
                    Task Log
                    <div class="badge btn " onclick="sendActionEvent('LOAD_LOG', '${{item.path}}', 'LOAD_LOG')">Load log</div>
                    
                    </div>
                    ${{buildTaskLogHTML(item.path)}}
                </div>`;

                const fileActionCard = buildActionCardHTML(
                FILE_ACTIONS, 'fileActionSel', 'fileActionDesc'
                );

                const downloadBtn = `
                <div class="stat" style="cursor:pointer; border-color: #21c55d33; background: #21c55d0a;"
                    onclick="sendActionEvent('DOWNLOAD', '${{item.path}}', 'DOWNLOAD')">
                    <div class="slabel">Download</div>
                    <div class="sval">Get File</div>
                </div>`;

                p.innerHTML = `
                ${{header}}
                <div class="stats">
                    <div class="stat"><div class="slabel">Type</div><div class="sval">${{ext || 'File'}}</div></div>
                    <div class="stat"><div class="slabel">Size</div><div class="sval">${{fmtSize(item.size)}}</div></div>
                    ${{downloadBtn}}
                </div>
                ${{taskLogCard}}
                ${{contentCard}}
                ${{fileActionCard}}
                `;
            }}
            }}

            function focusNode(path) {{
            expandParentsToPath(path);
            const found = allNodes.find(n => n.row.dataset.path === path);
            if (found) found.row.click();
            }}

            function expandParentsToPath(path) {{
            if (!path) return;
            const normalizedRoot    = ROOT.endsWith('/') || ROOT.endsWith('\\\\') ? ROOT.slice(0, -1) : ROOT;
            const normalizedPath    = path.split('\\\\').join('/');
            const normalizedRootFwd = normalizedRoot.split('\\\\').join('/');
            const relativePath = normalizedPath.startsWith(normalizedRootFwd)
                ? normalizedPath.slice(normalizedRootFwd.length) : normalizedPath;
            const pathParts = relativePath.split('/').filter(p => p);
            let currentPath     = normalizedRoot;
            let currentChildren = TREE;
            for (let i = 0; i < pathParts.length - 1; i++) {{
                const part = pathParts[i];
                currentPath += '/' + part;
                const found = currentChildren.find(item => item.name === part && item.is_dir);
                if (!found) break;
                const node = allNodes.find(n => n.item.path === currentPath);
                if (node) {{
                const wrap       = node.row.parentElement;
                const childrenEl = wrap ? wrap.querySelector('.children') : null;
                const toggle     = node.row.querySelector('.toggle');
                const iconEl     = node.row.querySelector('.file-icon');
                if (childrenEl && !childrenEl.classList.contains('open')) {{
                    childrenEl.classList.add('open');
                    if (toggle) toggle.textContent = '▼';
                    if (iconEl)  iconEl.textContent = '📂';
                }}
                }}
                currentChildren = found.children || [];
            }}
            }}

            function selectInitialNode(path) {{
                if (!path) return;
                expandParentsToPath(path);
                const found = allNodes.find(n => n.row.dataset.path === path);
                if (found) {{
                    found.row.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    found.row.click();
                }}
            }}

            // ── Search ────────────────────────────────────────────────
            function filterTree(q) {{
            if (!q) collapseAll(); else expandAll();
            const lq = q.toLowerCase();
            allNodes.forEach(({{ row }}) => {{
                row.style.display = (!lq || row.dataset.nameLower.includes(lq)) ? '' : 'none';
            }});
            }}

            // ── Expand / Collapse ─────────────────────────────────────
            function expandAll() {{
            document.querySelectorAll('.children').forEach(c => c.classList.add('open'));
            document.querySelectorAll('.toggle').forEach(t => {{ if (t.textContent) t.textContent = '▼'; }});
            }}
            function collapseAll() {{
            document.querySelectorAll('.children').forEach(c => c.classList.remove('open'));
            document.querySelectorAll('.toggle').forEach(t => {{ if (t.textContent) t.textContent = '▶'; }});
            }}
            function selectInitialNodeWhenReady(path, retries = 10) {{
                if (!path) return;
                expandParentsToPath(path);
                const found = allNodes.find(n => n.row.dataset.path === path);
                if (found) {{
                    found.row.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    found.row.click();
                }} else if (retries > 0) {{
                    setTimeout(() => selectInitialNodeWhenReady(path, retries - 1), 50);
                }}
            }}  


            // ── Init ──────────────────────────────────────────────────
            buildTree(TREE, document.getElementById('treePanel'));
            isLightMode = localStorage.getItem('fileExplorerLightMode') === 'true';
            document.body.classList.toggle('light-mode', isLightMode);
            
            if (window.Streamlit) window.Streamlit.setFrameHeight();
            </script>
            <script>
                function sendMessageToStreamlitClient(type, data) {{
                var outData = Object.assign({{ isStreamlitMessage: true, type: type }}, data);
                window.parent.postMessage(outData, "*");
                }}
                function init() {{
                sendMessageToStreamlitClient("streamlit:componentReady", {{apiVersion: 1}});
                }}
                function sendDataToPython(data) {{
                sendMessageToStreamlitClient("streamlit:setComponentValue", data);
                }}
                function onDataFromPython(event) {{
                    console.log(event);
                if (event.data.type !== "streamlit:render") return;
                if (event.data.args.log){{
                    FILE_TASK_LOG = event.data.args.log;
                }}
                if (event.data.args.initial_selection){{
                    console.log(event.data.args.initial_selection);
                    INITIAL_SELECTION = event.data.args.initial_selection;                    
                }}
                if (event.data.args.content) {{
                    FILE_CONTENT = event.data.args.content;  // ← dict {{path: "content string"}}
                }}
                requestAnimationFrame(() => selectInitialNode(INITIAL_SELECTION));
                }}
                window.addEventListener("message", onDataFromPython);
                init();
                window.addEventListener("load", function() {{
                //window.setTimeout(function() {{ setFrameHeight(document.documentElement.clientHeight); }}, 0);
                }});
                //setFrameHeight(0);
            </script>
            </body>
            </html>"""

        return html

    @staticmethod
    def create_file_explorer_component(html_content: str = None, is_light="true"):
        if not html_content:
            html_content = OsirWebFile.file_explorer(
                root_path=str(OSIR_PATHS.CASES_DIR),
                file_actions=OsirWebFile.get_all_module(),
                folder_actions=OsirWebFile.get_all_module(for_file=False),
                light_mode=is_light
            )
        component_dir = os.path.dirname(__file__)
        component_path = os.path.join(component_dir, 'dynamic')
        
        if not os.path.exists(component_path):
            os.makedirs(component_path)
        
        index_html_path = os.path.join(component_path, "index.html")

        with open(index_html_path, "w") as f:
            f.write(html_content)

        return components.declare_component(
            "file_explorer",
            path=component_path
        )

    @staticmethod
    def _build_tree(path, max_depth=4, current_depth=0):
        """Recursively build a directory tree."""
        if current_depth >= max_depth:
            return []
        items = []
        try:
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                if entry.name.startswith('.'):
                    continue
                item = {
                    "name": entry.name,
                    "path": entry.path,
                    "is_dir": entry.is_dir(),
                    "size": 0,
                    "children": []
                }
                try:
                    if entry.is_file():
                        item["size"] = entry.stat().st_size
                except OSError:
                    pass
                if entry.is_dir():
                    item["children"] = OsirWebFile._build_tree(entry.path, max_depth, current_depth + 1)
                items.append(item)
        except PermissionError:
            pass
        return items

import socket
import json
import threading
import time
import re
import os
from pydantic import BaseModel

from osir_lib.core.FileManager import FileManager
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_service.ipc.OsirIpcTus import OsirIpcTus
from osir_service.ipc.model.OsirExceptions import OsirException
from osir_service.ipc.model.OsirIpcResponse import OsirIpcResponse
from osir_service.ipc.model.OsirIpcRequest import OsirIpcRequest
from osir_service.postgres.OsirDb import OsirDb
from osir_service.watchdog.MonitorCase import MonitorCase
from osir_service.ipc.OsirSocket import OsirSocket
from osir_service.postgres.model.OsirDbHandlerModel import OsirDbHandlerModel
from osir_service.orchestration.TaskService import TaskService
from osir_service.ipc.model.OsirFileModel import FsData
from osir_service.ipc.model.OsirAction import OSIR_ACTIONS, register_action
from osir_service.ipc.OsirIpcFiles import OsirIpcFiles

from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()


class OsirIpc(BaseModel):
    """
    Core IPC (Inter-Process Communication) service for the OSIR framework.
    Listens on a TCP socket and dispatches JSON requests to registered action handlers.
    """

    host: str
    port: int
    
    _files_handler: OsirIpcFiles = OsirIpcFiles()
    _tus_handler: OsirIpcTus = OsirIpcTus()

    def listen(self):
        """
        Main server loop that maintains the TCP socket.

        Handles incoming connections and ensures the server automatically
        restarts in case of a critical failure.
        """
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((self.host, self.port))
                    s.listen()
                    logger.info(f"Listening on {self.host}:{self.port}")
                    self._accept_loop(s)
            except Exception as e:
                logger.error(f"Server crashed: {e}. Restarting in 5 seconds...")
                time.sleep(5)

    def _accept_loop(self, s: socket.socket):
        """Accepts and handles incoming client connections."""
        while True:
            try:
                conn, addr = s.accept()
                threading.Thread(target=self._request_loop, args=(conn,)).start()
                
                # logger.info(f"Connected by {addr}")
                # with conn:
                #     self._request_loop(conn)
            except Exception as e:
                logger.error(f"Error accepting connection: {e}")
                continue

    def _request_loop(self, conn: socket.socket):
        """Processes incoming requests on an established connection."""
        while True:
            try:
                request = OsirSocket.recv_json(conn)
                response = self.action(request)
                
                if response is not None:
                    OsirSocket.send_json(conn, response, pydantic=True)
                
            except ConnectionError:
                break
            except Exception as e:
                logger.error_handler(f"Error handling request: {e}")
                break

    def start(self):
        """Launches the IPC listener in a dedicated background thread."""
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()
        return thread

    def action(self, request: dict):
        """
        Dispatches incoming JSON requests to the appropriate registered handler.

        Args:
            request (dict): The raw JSON request from the IPC client.

        Returns:
            OsirIpcResponse: A standardized response object or an OsirException.
        """
        try:
            
            osir_ipc_request = OsirIpcRequest(**request)

            osir_ipc_response = OsirIpcResponse(response={})
            
            osir_action = OSIR_ACTIONS.get(osir_ipc_request.action)

            if not osir_action:
                return OsirException.UNKNOWN_ACTION(action=osir_ipc_request.action)

            params = osir_ipc_request.params or {}
            for field in osir_action["required_fields"]:
                if not params.get(field):
                    return OsirException.MISSING_PARAMETER(parameter_name=field)

            result = osir_action["handler"](self, osir_ipc_request, osir_ipc_response)
            # If handler returns a response, use it. Otherwise fall back to the default response.
            if result is not None:
                osir_ipc_response = result
        except Exception as e:
            logger.error(
                f"Error while processing IPC request:\n"
                f"{json.dumps(request, indent=4, ensure_ascii=False)}\n"
            )
            logger.error_handler(e)
            return OsirException.UNEXPECTED_ERROR(str(e))

        return osir_ipc_response

    # TODO: Remove this to handle this logique inside MonitorCase 
    def _start_background_handler(self, monitor: MonitorCase) -> tuple:
        """Starts a MonitorCase handler in a background thread and returns (handler_uuid, case_uuid)."""
        threading.Thread(target=monitor.setup_handler, daemon=True).start()
        return monitor.handler_uuid, monitor.case_uuid

    @register_action('socket_on')
    def _handle_socket_on(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        resp.message = "SOCKET READY"
        return resp

    @register_action('exec_module', required_fields=['modules', 'case_path'])
    def _handle_exec_module(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        if req.params.get('input_path'):
            # TODO: Security check on input file
            module_model = OsirModuleModel.from_name(req.params['modules'][0])
            module_model.input.match = req.params['input_path']
            case_path = re.match(r'^(.*?/cases/[^/]+)', req.params['input_path']).group(1)

            with OsirDb() as db:
                case_uuid = db.case.get(name=os.path.basename(case_path)).case_uuid
            
            task_id = TaskService.push_task(case_path=case_path, module_instance=module_model, case_uuid=case_uuid)
            
            with OsirDb() as db:
                resp.message = "Module execution started"
                resp.response = db.task.get(task_id=task_id)
        else:
            monitor = MonitorCase(case_path=req.params['case_path'], modules=req.params['modules'], reprocess_case=True)
            handler_uuid, case_uuid = self._start_background_handler(monitor)
            resp.message = "Module execution started"
            resp.response = OsirDbHandlerModel(
                handler_id=handler_uuid,
                case_uuid=case_uuid,
                task_id=[],
                modules=req.params['modules'],
                processing_status='processing_started',
            )
        return resp

    @register_action('exec_profile', required_fields=['profile'])
    def _handle_exec_profile(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        profile_data = req.params.get('profile')
        if isinstance(profile_data, str):
            from osir_lib.core.model.OsirProfileModel import OsirProfileModel
            profile_data = OsirProfileModel.from_name(profile_data)
        monitor = MonitorCase(case_path=req.params.get('case_path'), modules=profile_data.modules, reprocess_case=True)
        
        handler_uuid, case_uuid = self._start_background_handler(monitor)

        resp.message = "Profile execution started"
        resp.response = OsirDbHandlerModel(
            handler_id=handler_uuid,
            case_uuid=case_uuid,
            task_id=[],
            modules=profile_data.modules,
            processing_status='processing_started',
        )
        return resp

    @register_action('create_handler', required_fields=['case_name'])
    def _handle_create_handler(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        """Create a handler with profile/modules validation and start processing."""
        from osir_lib.core.model.OsirProfileModel import OsirProfileModel
        from osir_service.ipc.model.OsirExceptions import OsirException

        params = req.params
        profile_instance = params.get('profile', [])
        selected_modules = params.get('modules', [])
        modules_to_add = params.get('profile_module_to_add', [])
        modules_to_remove = params.get('profile_module_to_remove', [])
        selected_case = params.get('case_name', None)
        reprocess_case = params.get('reprocess', False)
        modified_modules = params.get('modified_modules', [])

        # Validate inputs
        if not profile_instance and not selected_modules:
            return OsirException.PROFILE_OR_MODULE_REQUIRED()

        if (modules_to_add or modules_to_remove) and not profile_instance:
            return OsirException.PROFILE_REQUIRED_FOR_MODULE_OPERATIONS()

        if (profile_instance or selected_modules) and not selected_case:
            return OsirException.CASE_REQUIRED()

        # Get case path and validate it exists
        case_path = FileManager.get_cases_path(selected_case)
        if not case_path or not case_path.exists():
            return OsirException.CASE_NOT_FOUND(selected_case)

        # Load or create profile instance
        if profile_instance:
            if isinstance(profile_instance, str):
                try:
                    profile_instance = OsirProfileModel.from_name(profile_instance)
                except Exception as e:
                    return OsirException.MODULE_LOAD_ERROR(str(e))
            # Apply module modifications
            profile_instance.remove_modules(modules_to_remove)
            profile_instance.add_modules(modules_to_add)
            modules = profile_instance.modules
        else:
            modules = selected_modules

        # Setup the monitor case
        monitor_case = MonitorCase(case_path=case_path, modules=modules, reprocess_case=reprocess_case)
        
        if modified_modules:
            for module in modified_modules:
                module_model = OsirModuleModel(**module)
                key = getattr(module_model, "filename", None)
                if not key:
                    continue
                for i, instance in enumerate(monitor_case.module_instances):
                    try:
                        if key == getattr(instance, "filename", None):
                            monitor_case.module_instances[i] = module_model
                    except Exception as e:
                        return OsirException.UNEXPECTED_ERROR(str(e))

        handler_uuid, case_uuid = self._start_background_handler(monitor_case)

        resp.message = "Handler created successfully"
        resp.response = {
            "handler_id": handler_uuid,
            "case_uuid": case_uuid,
            "case_name": selected_case,
            "modules": modules,
            "processing_status": "processing_started"
        }
        return resp

    @register_action('create_advanced_handler', required_fields=['case_name'])
    def _handle_create_advanced_handler(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        from osir_service.ipc.model.OsirExceptions import OsirException

        params = req.params
        files_module = params.get('files_modules')
        files_input = params.get('files_input', [])
        folders_modules = params.get('folders_modules')
        folders_input = params.get('folders_input', [])
        files_in_folder_modules = params.get('files_in_folder_modules')
        endpoint_name = params.get('endpoint_name')
        case_name = params.get('case_name', [])

        if not any([files_input, folders_input]):
            return OsirException.FILES_OR_FOLDERS_REQUIRED()

        if not case_name:
            return OsirException.CASE_NAME_REQUIRED()

        handler_uuid = None

        if files_input:
            if not files_module:
                return OsirException.MODULE_REQUIRED_FOR_FILES()
            for file in files_input:
                file_path = FsData.get_absolute_path(file)
                case_name, virt_path = FsData.get_real_path(file)
                module_instance = OsirModuleModel.from_name(files_module)
                module_instance.input.match = str(file_path)
                if endpoint_name:
                    module_instance.endpoint.default = endpoint_name
                monitor_case = MonitorCase(
                    case_path=str(FileManager.get_cases_path(case_name)),
                    modules=[],
                    reprocess_case=True
                )
                case_uuid = monitor_case.case_uuid
                handler_uuid = monitor_case.run_task(module_instance, handler_uuid)

        if folders_input:
            if not folders_modules and not files_in_folder_modules:
                return OsirException.MODULE_REQUIRED_FOR_FOLDERS()
            for folder in folders_input:
                folder_path = FsData.get_absolute_path(folder)
                case_name, virt_path = FsData.get_real_path(folder)
                if folders_modules:
                    module_instance = OsirModuleModel.from_name(folders_modules)
                    module_instance.input.match = str(folder_path)
                    if endpoint_name:
                        module_instance.endpoint.default = endpoint_name
                    monitor_case = MonitorCase(
                        case_path=str(FileManager.get_cases_path(case_name)),
                        modules=[],
                        reprocess_case=True
                    )
                    case_uuid = monitor_case.case_uuid
                    handler_uuid = monitor_case.run_task(module_instance, handler_uuid)
                if files_in_folder_modules:
                    for file in FileManager.get_subfiles(folder_path):
                        module_instance = OsirModuleModel.from_name(files_in_folder_modules)
                        module_instance.input.match = str(file)
                        if endpoint_name:
                            module_instance.endpoint.default = endpoint_name
                        monitor_case = MonitorCase(
                            case_path=str(FileManager.get_cases_path(case_name)),
                            modules=[],
                            reprocess_case=True
                        )
                        case_uuid = monitor_case.case_uuid
                        handler_uuid = monitor_case.run_task(module_instance, handler_uuid)

        resp.message = "Handler created successfully"
        resp.response = {
            "handler_id": handler_uuid,
            "case_uuid": case_uuid,
            "case_name": case_name,
            "modules": [module for module in [files_in_folder_modules, folders_modules, files_module] if module],
            "processing_status": "processing_started"
        }
        return resp

    @register_action('delete_handler', required_fields=['handler_uuid'])
    def _handle_delete_handler(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        
        handler_uuid = req.params["handler_uuid"]

        with OsirDb() as db:
            to_delete = db.handler.get(handler_id=handler_uuid)

            if to_delete:
                db.task.delete(handler_id=handler_uuid)
                db.handler.delete(handler_id=handler_uuid)

        resp.response = to_delete
        return resp
    
    @register_action('create_case', required_fields=['case_name'])
    def _handle_create_case(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        with OsirDb() as db:
            resp.response = db.case.create(name=req.params['case_name'])
        return resp

    @register_action('get_cases')
    def _handle_get_cases(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        from osir_service.postgres.model.OsirDbCaseModel import OsirDbCaseModel

        with OsirDb() as db:
            all_cases_in_db = db.case.list()
            for case in FileManager.all_cases():
                if case not in [c.name for c in all_cases_in_db]:
                    all_cases_in_db.append(db.case.create(name=case))
            resp.response = all_cases_in_db
        return resp

    @register_action('get_tasks', required_fields=['case_name'])
    def _handle_get_tasks(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        with OsirDb() as db:
            case_uuid = req.params.get('case_uuid')
            if not case_uuid:
                case_uuid = db.case.get(name=req.params['case_name']).case_uuid
            resp.message = "Tasks retrieved"
            resp.response = db.task.list(case_uuid=case_uuid)
        return resp

    @register_action('get_task_log', required_fields=['task_id'])
    def _handle_get_task_log(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        with OsirDb() as db:
            result = db.task.get(req.params['task_id'])
        resp.message = "Task log retrieved"
        resp.response = result if result else {"task_id": req.params['task_id']}
        return resp

    @register_action('get_handler_status', required_fields=['handler_id'])
    def _handle_get_handler_status(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        with OsirDb() as db:
            resp.message = "Handler Status retrieved"
            resp.response = db.handler.get(handler_id=req.params['handler_id'])
        return resp

    @register_action('get_case_handler', required_fields=['case_name'])
    def _handle_get_case_handler(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        with OsirDb() as db:
            case_uuid = req.params.get('case_uuid')
            if not case_uuid:
                case_uuid = db.case.get(name=req.params['case_name']).case_uuid
            if not case_uuid:
                resp.response = "ERROR: CASE NOT FOUND"
                return resp
            resp.message = "Handlers retrieved"
            resp.response = db.handler.get(case_uuid=case_uuid)

            if not isinstance(resp.response, list):
                resp.response = [resp.response]

        return resp

    @register_action('get_handler_task_info')
    def _handle_get_handler_task_info(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        with OsirDb() as db:
            result = db.handler.get_all_task_logs(req.params['handler_id'])
        resp.message = "Handler Task log retrieved"
        resp.response = result if result else []
        return resp

    @register_action('get_modules')
    def _handle_get_modules(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        resp.message = "Modules retrieved"
        resp.response = FileManager.all_modules(relative=True)
        return resp

    @register_action('get_module_info', required_fields=['modules'])
    def _handle_get_module_info(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        keys = req.params.get('keys', ['all'])
        result = {}
        for module_name in req.params['modules']:
            try:
                model_data = OsirModuleModel.from_name(module_name).model_dump()
                if "all" not in keys:
                    filtered_data = {k: v for k, v in model_data.items() if k in keys}
                    result[module_name] = filtered_data
                else:
                    result[module_name] = model_data
            except Exception as e:
                logger.error(f"Error loading module {module_name}: {e}")
                result[module_name] = {}

        resp.message = "Module Info Retrieved." if result else "No modules found."
        resp.response = result
        return resp

    @register_action('files_list')
    def _handle_files_list(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        return self._files_handler.handle_files_list(req, resp)

    @register_action('files_delete', required_fields=['body'])
    def _handle_files_delete(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        return self._files_handler.handle_files_delete(req, resp)

    @register_action('files_rename', required_fields=['body'])
    def _handle_files_rename(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        return self._files_handler.handle_files_rename(req, resp)

    @register_action('files_copy', required_fields=['body'])
    def _handle_files_copy(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        return self._files_handler.handle_files_copy(req, resp)

    @register_action('files_move', required_fields=['body'])
    def _handle_files_move(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        return self._files_handler.handle_files_move(req, resp)

    @register_action('files_archive', required_fields=['body'])
    def _handle_files_archive(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        return self._files_handler.handle_files_archive(req, resp)

    @register_action('files_unarchive', required_fields=['body'])
    def _handle_files_unarchive(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        return self._files_handler.handle_files_unarchive(req, resp)

    @register_action('files_create_folder', required_fields=['body'])
    def _handle_files_create_folder(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        return self._files_handler.handle_files_create_folder(req, resp)

    @register_action('files_download', required_fields=['path'])
    def _handle_files_download(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        return self._files_handler.handle_files_download(req, resp)

    @register_action('files_search', required_fields=['path'])
    def _handle_files_search(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        return self._files_handler.handle_files_search(req, resp)

    @register_action('tus_upload_options')
    def _handle_tus_upload_options(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        return self._tus_handler.handle_tus_upload_options(req, resp)
    
    @register_action('tus_upload_post')
    def _handle_tus_upload_post(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        return self._tus_handler.handle_tus_upload_post(req, resp)
    
    @register_action('tus_upload_patch')
    def _handle_tus_upload_patch(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        return self._tus_handler.handle_tus_upload_patch(req, resp)

    @register_action('tus_upload_head', required_fields=['uuid'])
    def _handle_tus_upload_head(self, req: OsirIpcRequest, resp: OsirIpcResponse):
        return self._tus_handler.handle_tus_upload_head(req, resp)

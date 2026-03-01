import socket
import json
import threading
import time
import re
import os
from pydantic import BaseModel

from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirUtils import get_latest_log_by_task_id
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_service.ipc.OsirExceptions import OsirException
from osir_service.ipc.OsirIpcModel import OsirIpcModel, OsirIpcResponse
from osir_service.ipc.OsirIpc import OsirIpc
from osir_service.postgres.OsirDb import OsirDb
from osir_service.watchdog.MonitorCase import MonitorCase
from osir_service.ipc.JsonSocket import recv_json, send_json
from osir_service.postgres.model.OsirDbHandlerModel import OsirDbHandlerModel
from osir_service.orchestration.TaskService import TaskService

from osir_lib.core.OsirConstants import OSIR, OSIR_PATHS
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()


class IpcService(BaseModel):
    """
        Core IPC (Inter-Process Communication) service for the OSIR framework.
    """
    host: str
    port: int

    def listen(self):
        """
            Main server loop that maintains the TCP socket.

            Handles incoming connections and ensures the server automatically 
            restarts in case of a critical failure.
        """
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    # Prevents "Address already in use" errors during quick restarts
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((self.host, self.port))
                    s.listen()
                    logger.info(f"Listening on {self.host}:{self.port}")
                    while True:
                        try:
                            conn, addr = s.accept()
                            logger.info(f"Connected by {addr}")
                            with conn:
                                while True:
                                    try:
                                        request = recv_json(conn)
                                        # logger.debug(f"Received JSON: {request}")
                                        response = self.action(request)
                                        if response is not None:
                                            send_json(conn, response, pydantic=True)
                                            # logger.info(f"Sent IPC response to client: {response}")
                                    except ConnectionError:
                                        logger.debug("Client disconnected.")
                                        break
                                    except Exception as e:
                                        logger.error(f"Error handling request: {e}")
                                        break
                        except Exception as e:
                            logger.error(f"Error accepting connection: {e}")
                            continue
            except Exception as e:
                logger.error(f"Server crashed: {e}. Restarting in 5 seconds...")
                time.sleep(5)

    def start(self):
        """Launches the IPC listener in a dedicated background thread."""
        threading.Thread(target=self.listen, daemon=True).start()

    @staticmethod
    def consume_generator(g):
        """
            Utility to consume a generator in a background thread.
            Used to execute module setup logic after returning the initial handler UUID.
        """
        try:
            for _ in g:
                pass
        except Exception as e:
            logger.error(f"Error in background handler: {e}")

    def action(self, request: dict):
        """
            Dispatches incoming JSON requests to the appropriate action.

            Args:
                request (dict): The raw JSON request from the IPC client.

            Returns:
                OsirIpcResponse: A standardized response object or an OsirException.
        """
        try:
            osir_ipc_model = OsirIpcModel(**request)
            osir_ipc_request = OsirIpc(**osir_ipc_model.model_dump())

            # Initialize base response object
            osir_ipc_response = OsirIpcResponse(
                version=OSIR.VERSION,
                status=200,
                response={}
            )

            match osir_ipc_request.action:
                case 'socket_on':
                    osir_ipc_response.message = "SOCKET READY"

                case 'exec_module':
                    if not hasattr(osir_ipc_request, "modules") or not osir_ipc_request.modules:
                        return OsirException.MISSING_PARAMETER(parameter_name="modules")
                    if not hasattr(osir_ipc_request, "case_path") or not osir_ipc_request.case_path:
                        return OsirException.CASE_NOT_FOUND(case=osir_ipc_model.case_name)

                    if hasattr(osir_ipc_request, "input_path") and osir_ipc_request.input_path:
                        # TODO: Security check on input file
                        module_model = OsirModuleModel.from_name(osir_ipc_request.modules[0])
                        module_model.input.match = osir_ipc_request.input_path
                        case_path = re.match(r'^(.*?/cases/[^/]+)', osir_ipc_request.input_path).group(1)
                        with OsirDb() as db:
                            case_uuid = db.case.get(name=os.path.basename(case_path)).case_uuid
                        task_id = TaskService.push_task(case_path=case_path,module_instance=module_model,case_uuid=case_uuid)
                        with OsirDb() as db:
                            osir_ipc_response.message = "Module execution started"
                            osir_ipc_response.response = db.task.get(task_id=task_id)
                    else:
                        # Trigger background module execution
                        gen = self.action_exec_module(osir_ipc_request)
                        handler_uuid, case_uuid = next(gen)
                        threading.Thread(target=self.consume_generator, args=(gen,), daemon=True).start()

                        osir_ipc_response.message = "Module execution started"
                        osir_ipc_response.response = OsirDbHandlerModel(
                            handler_id=handler_uuid,
                            case_uuid=case_uuid,
                            task_id=[],
                            modules=osir_ipc_request.modules,
                            processing_status='processing_started',
                        )

                case 'exec_profile':
                    if not hasattr(osir_ipc_request, "profile") or not osir_ipc_request.profile:
                        return OsirException.MISSING_PARAMETER(parameter_name="profile")

                    gen = self.action_exec_profile(osir_ipc_request)
                    handler_uuid, case_uuid = next(gen)
                    threading.Thread(target=self.consume_generator, args=(gen,), daemon=True).start()

                    osir_ipc_response.response["message"] = "Profile execution started"
                    osir_ipc_response.response = OsirDbHandlerModel(
                        handler_id=handler_uuid,
                        case_uuid=case_uuid,
                        task_id=[],
                        modules=osir_ipc_request.profile.modules,
                        processing_status='processing_started',
                    )

                case 'create_case':
                    if not hasattr(osir_ipc_request, "case_name") or not osir_ipc_request.case_name:
                        return OsirException.MISSING_PARAMETER(parameter_name="case_name")
                    osir_ipc_response.response = self.action_create_case(osir_ipc_request)

                case 'get_cases':
                    osir_ipc_response.response = self.action_get_cases()

                case 'get_tasks':
                    if not hasattr(osir_ipc_request, "case_name") or not osir_ipc_request.case_name:
                        return OsirException.MISSING_PARAMETER(parameter_name="case_name")

                    osir_ipc_response.message = "Tasks retrieved"
                    osir_ipc_response.response = self.action_get_tasks(osir_ipc_request)

                case 'get_task_log':
                    if not hasattr(osir_ipc_request, "task_id") or not osir_ipc_request.task_id:
                        return OsirException.MISSING_PARAMETER(parameter_name="task_id")

                    osir_ipc_response.message = "Task log retrieved"
                    result = self.action_get_task_log(osir_ipc_request)
                    if result:
                        osir_ipc_response.response = result
                    else:
                        osir_ipc_response.response = {"task_id": osir_ipc_request.task_id}

                case 'get_handler_status':
                    if not hasattr(osir_ipc_request, "handler_id") or not osir_ipc_request.handler_id:
                        return OsirException.MISSING_PARAMETER(parameter_name="handler_id")

                    osir_ipc_response.message = "Handler Status retrieved"
                    osir_ipc_response.response = self.action_get_handler_status(osir_ipc_request)

                case 'get_case_handler':
                    if not hasattr(osir_ipc_request, "case_name") or not osir_ipc_request.case_name:
                        return OsirException.MISSING_PARAMETER(parameter_name="case_name")

                    osir_ipc_response.message = "Handler retrieved"
                    osir_ipc_response.response = self.action_get_case_handler(osir_ipc_request)

        except Exception as e:
            logger.error(
                f"Error while processing IPC request: \n"
                f"{json.dumps(request, indent=4, ensure_ascii=False)}\n"
            )
            logger.error_handler(e)
            return OsirException.UNEXPECTED_ERROR(str(e))

        return osir_ipc_response

    def action_exec_module(self, osir_ipc: OsirIpc):
        """Initializes a case monitor for specific module execution."""
        handler_module = MonitorCase(case_path=osir_ipc.case_path, modules=osir_ipc.modules, reprocess_case=True)
        yield (handler_module.handler_uuid, handler_module.case_uuid)
        handler_module.setup_handler()

    def action_exec_profile(self, osir_ipc: OsirIpc):
        """Initializes a case monitor for profile-based execution."""
        handler_profile = MonitorCase(case_path=osir_ipc.case_path, modules=osir_ipc.profile.modules, reprocess_case=True)
        yield (handler_profile.handler_uuid, handler_profile.case_uuid)
        handler_profile.setup_handler()

    def action_create_case(self, osir_ipc: OsirIpc):
        """Handles database and filesystem creation for a new forensic case."""
        with OsirDb() as db:
            return db.case.create(name=osir_ipc.case_name)

    def action_get_task_log(self, osir_ipc: OsirIpc):
        """Queries the JSONL log files for specific task traces."""
        with OsirDb() as db:
            return db.task.get(osir_ipc.task_id)

    def action_get_tasks(self, osir_ipc: OsirIpc):
        with OsirDb() as db:
            if not osir_ipc.case_uuid:
                osir_ipc.case_uuid = db.case.get(name=osir_ipc.case_name).case_uuid
            return db.task.list(case_uuid=osir_ipc.case_uuid)
    
    def action_get_cases(self):
        with OsirDb() as db:
            return db.case.list()

    def action_get_handler_status(self, osir_ipc: OsirIpc):
        with OsirDb() as db:
            return db.handler.get(handler_id=osir_ipc.handler_id)

    def action_get_case_handler(self, osir_ipc: OsirIpc):
        """Returns all handlers associated with a specific case."""
        with OsirDb() as db:
            if not osir_ipc.case_uuid:
                osir_ipc.case_uuid = db.case.get(name=osir_ipc.case_name).case_uuid

            if not osir_ipc.case_uuid:
                return "ERROR: CASE NOT FOUND"

            return db.handler.get(case_uuid=osir_ipc.case_uuid)

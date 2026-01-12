import socket
import json
import threading
import time
from pydantic import BaseModel

from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirUtils import get_latest_log_by_task_id
from osir_lib.core.model.OsirModuleModel import OsirModuleModel
from osir_service.ipc.OsirExceptions import OsirException
from osir_service.ipc.OsirIpcModel import OsirIpcModel, OsirIpcResponse
from osir_service.ipc.OsirIpc import OsirIpc
from osir_service.postgres.PostgresService import OSIR_DB
from osir_service.watchdog.MonitorCase import MonitorCase
from osir_service.ipc.JsonSocket import recv_json, send_json
from osir_lib.core.OsirConstants import OSIR, OSIR_PATHS
from osir_lib.logger import AppLogger

logger = AppLogger(__name__).get_logger()

class IpcService(BaseModel):
    host: str
    port: int

    def listen(self):
        while True:  
            try: 
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Évite les erreurs "Address already in use"
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
                                        logger.debug(f"Received JSON: {request}")
                                        response = self.action(request)
                                        if response is not None:
                                            send_json(conn, response, pydantic=True)
                                            logger.info("The IPC Server answer the client {response}")
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
        threading.Thread(target=self.listen, daemon=True).start()

    @staticmethod
    def consume_generator(g):
        try:
            for _ in g: pass # Exécute tout ce qui reste après le yield
        except Exception as e:
            logger.error(f"Error in background handler: {e}")

    def action(self, request: dict):
        """Traite la requête JSON et renvoie un JSON"""
        try: 
            osir_ipc_model = OsirIpcModel(**request)
            osir_ipc_request = OsirIpc(**osir_ipc_model.model_dump())
            
            # Initialisation de la réponse de base
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
                    
                    gen = self.action_exec_module(osir_ipc_request)
                    handler_uuid = next(gen) 
                    threading.Thread(target=self.consume_generator, args=(gen,), daemon=True).start()

                    osir_ipc_response.message = "Module execution started"
                    osir_ipc_response.response["handler_id"] = handler_uuid

                case 'exec_profile':
                    if not hasattr(osir_ipc_request, "profile") or not osir_ipc_request.profile:
                        return OsirException.MISSING_PARAMETER(parameter_name="profile")

                    gen = self.action_exec_profile(osir_ipc_request)
                    handler_uuid = next(gen)
                    threading.Thread(target=self.consume_generator, args=(gen,), daemon=True).start()
                    
                    osir_ipc_response.response["message"] = "Module execution started"
                    osir_ipc_response.response["handler_id"] = handler_uuid

                case 'create_case':
                    if not hasattr(osir_ipc_request, "case_name") or not osir_ipc_request.case_name:
                        return OsirException.MISSING_PARAMETER(parameter_name="case_name")
                    osir_ipc_response.response = self.action_create_case(osir_ipc_request)

                case 'get_task_log':
                    if not hasattr(osir_ipc_request, "task_id") or not osir_ipc_request.task_id:
                        return OsirException.MISSING_PARAMETER(parameter_name="task_id")

                    osir_ipc_response.message = "Task log retrieved"
                    result = self.action_get_task_log(osir_ipc_request)
                    if result:
                        osir_ipc_response.response =  self.action_get_task_log(osir_ipc_request)
                    else:
                        osir_ipc_response.response = {"task_id":osir_ipc_request.task_id}

                case 'get_handler_status':
                    if not hasattr(osir_ipc_request, "handler_id") or not osir_ipc_request.handler_id:
                        return OsirException.MISSING_PARAMETER(parameter_name="handler_id")
                    
                    osir_ipc_response.message = "Handler Status retrieved"
                    osir_ipc_response.response = self.action_get_handler_status(osir_ipc_request)

                case 'get_case_handler':
                    if not hasattr(osir_ipc_request, "case_name") or not osir_ipc_request.case_name:
                        return OsirException.MISSING_PARAMETER(parameter_name="case_name")
                    
                    osir_ipc_response.message = "Handler retrieved"
                    osir_ipc_response.response["handlers"] = self.action_get_case_handler(osir_ipc_request)

        except Exception as e:
            logger.error(
                f"Error while processing: \n"
                f"{json.dumps(request, indent=4, ensure_ascii=False)}\n"
            )
            logger.error_handler(e)
            return OsirException.UNEXPECTED_ERROR(str(e))

        return osir_ipc_response

    def action_exec_module(self, osir_ipc: OsirIpc):
        handler_module = MonitorCase(case_path=osir_ipc.case_path, modules=osir_ipc.modules, reprocess_case=True)
        yield handler_module.handler_uuid
        handler_module.setup_handler()
    
    def action_exec_profile(self, osir_ipc: OsirIpc):
        handler_profile = MonitorCase(case_path=osir_ipc.case_path, modules=osir_ipc.profile.modules, reprocess_case=True)
        yield handler_profile.handler_uuid
        logger.info("test")

        handler_profile.setup_handler()

    def action_create_case(self, osir_ipc: OsirIpc):
        case_uuid = OSIR_DB.case.create(name=osir_ipc.case_name)
        if case_uuid:
            state, case_path = FileManager.create_case(OSIR_PATHS.CASES_DIR, case_name=osir_ipc.case_name)
        
        # TODO : Replace with class from OSIR_LIB
        return {
            "case_name": osir_ipc.case_name,
            "case_uuid": case_uuid,
            "case_path": case_path,
            "state": state
        }
    
    def action_get_task_log(self, osir_ipc: OsirIpc):
        log_file = OSIR_PATHS.LOG_DIR / "task_traces.jsonl"
        return get_latest_log_by_task_id(osir_ipc.task_id, log_file)

    def action_get_handler_status(self, osir_ipc: OsirIpc):
        return OSIR_DB.handler.get(handler_id=osir_ipc.handler_id)
    
    def action_get_case_handler(self, osir_ipc: OsirIpc):
        if not osir_ipc.case_uuid:
            osir_ipc.case_uuid = OSIR_DB.case.get(name=osir_ipc.case_name)

        if not osir_ipc.case_uuid:
            return "ERROR: CASE NOT FOUND"

        return OSIR_DB.handler.get(case_uuid=osir_ipc.case_uuid)
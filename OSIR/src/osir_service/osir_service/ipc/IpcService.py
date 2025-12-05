import socket
import json
import threading
from pydantic import BaseModel

from osir_lib.logger import AppLogger
from osir_service.ipc.OsirIpcModel import OsirIpcModel
from osir_service.watchdog.MonitorCase import MonitorCase
from osir_service.ipc.JsonSocket import recv_json, send_json

logger = AppLogger(__name__).get_logger()

class IpcService(BaseModel):
    host: str
    port: int

    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            logger.info(f"Listening on {self.host}:{self.port}")

            while True:
                conn, addr = s.accept()
                logger.info(f"Connected by {addr}")
                with conn:
                    while True:
                        try:
                            request = recv_json(conn)
                            logger.debug(f"Received JSON: {request}")
                            response = self.action(request)
                            if response is not None:
                                send_json(conn, response)
                                logger.info("The IPC Server answer the client")
                        except ConnectionError:
                            logger.debug("Client disconnected.")
                            break
                            

    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()

    def action(self, request: dict):
        """Traite la requête JSON et renvoie un JSON"""
        osir_ipc = OsirIpcModel(**request)

        match osir_ipc.action:
            case 'exec_module':
                self.action_exec_module(osir_ipc)
        # exemple de réponse JSON :
        return {"status": "ok", "received": request}

    def action_exec_module(self, osir_ipc: OsirIpcModel):
        MonitorCase(case_path=osir_ipc.case_path, modules=osir_ipc.modules, reprocess_case=True).setup_handler()
from pydantic import BaseModel

from osir_service.ipc.JsonSocket import send_and_receive
from osir_service.ipc.OsirIpcModel import OsirIpcModel

class OsirIpcClient(BaseModel):
    host: str = "master-master"
    port: int = 8989

    def send(self, osir_ipc: OsirIpcModel):
        return send_and_receive(self.host, self.port, osir_ipc.model_dump())

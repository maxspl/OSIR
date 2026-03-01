from pydantic import BaseModel

from osir_service.ipc.JsonSocket import send_and_receive
from osir_service.ipc.OsirIpcModel import OsirIpcModel


class OsirIpcClient(BaseModel):
    """
        The primary client-side interface for communicating with the OSIR Master service.

        Attributes:
            host (str): The hostname or IP address of the OSIR Master node. 
                Defaults to 'master-master' (internal Docker networking).
            port (int): The TCP port the IpcService is listening on. Defaults to 8989.
    """
    host: str = "master-master"
    port: int = 8989

    def send(self, osir_ipc: OsirIpcModel) -> str:
        """
            Serializes and transmits an IPC model to the Master node.

            Args:
                osir_ipc (OsirIpcModel): The validated request object containing 
                    the action and required parameters.

            Returns:
                str: The JSON-formatted response string from the Master service.
        """
        return send_and_receive(self.host, self.port, osir_ipc.model_dump())

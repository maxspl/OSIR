import json
import socket
from typing import Generator

from pydantic import BaseModel

from osir_service.ipc.model.OsirIpcRequest import OsirIpcRequest


class OsirSocket(BaseModel):
    """
        Handles low-level JSON socket communication for the OSIR IPC layer.

        Attributes:
            host (str): The hostname or IP address of the OSIR Master node.
                Defaults to 'master-master' (internal Docker networking).
            port (int): The TCP port the OsirIpc is listening on. Defaults to 8989.
    """
    host: str = "master-master"
    port: int = 8989

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    
    @staticmethod
    def _recv_exact(conn, num_bytes) -> bytes:
        """
            Ensures that exactly the requested number of bytes are read from the socket.

            Args:
                conn (socket.socket): The active network connection.
                num_bytes (int): Total bytes to read.

            Returns:
                bytes: The complete byte buffer.
        """
        buffer = b""
        while len(buffer) < num_bytes:
            chunk = conn.recv(num_bytes - len(buffer))
            if not chunk:
                raise ConnectionError("Socket closed prematurely by the remote host.")
            buffer += chunk
        return buffer

    @staticmethod
    def recv_json(conn) -> dict:
        """
            Receives and decodes a JSON object using a 4-byte big-endian header.
        """
        header = OsirSocket._recv_exact(conn, 4)
        size = int.from_bytes(header, "big")
        payload = OsirSocket._recv_exact(conn, size)
        return json.loads(payload.decode("utf-8"))

    @staticmethod
    def recv_message(conn) -> tuple[dict, Generator]:
        """Receives a unified message: JSON header + lazy binary body generator."""
        header_size = int.from_bytes(OsirSocket._recv_exact(conn, 4), "big")
        meta = json.loads(OsirSocket._recv_exact(conn, header_size).decode("utf-8"))
        body_size = meta.get("body_size", 0)

        def _stream_body():
            received = 0
            while received < body_size:
                chunk_size = int.from_bytes(OsirSocket._recv_exact(conn, 4), "big")
                if chunk_size == 0:
                    break
                chunk = OsirSocket._recv_exact(conn, chunk_size)
                received += chunk_size
                yield chunk

        return meta, _stream_body()

    @staticmethod
    def send_json(conn, obj, pydantic=False):
        """
            Serializes and sends a JSON object with a size-prefixed header.

            Args:
                conn (socket.socket): The connection to send data over.
                obj (Any): The object to serialize.
                pydantic (bool): If True, uses the model's native JSON serialization
                                to handle complex types like Paths or UUIDs.
        """
        if pydantic:
            data = obj.model_dump_json().encode("utf-8")
        else:
            data = json.dumps(obj).encode("utf-8")

        # Prepend a 4-byte big-endian size header
        size = len(data).to_bytes(4, "big")
        conn.sendall(size + data)

    def send(self, osir_ipc: OsirIpcRequest) -> str:
        """
            Serializes and transmits an IPC model to the Master node.

            Args:
                osir_ipc (OsirIpcRequest): The validated request object containing
                    the action and required parameters.

            Returns:
                str: The JSON-formatted response string from the Master service.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            self.send_json(s, osir_ipc.model_dump())
            reply = self.recv_json(s)
            return json.dumps(reply) + "\n"


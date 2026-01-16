import json
import socket


def recv_exact(conn, num_bytes):
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


def recv_json(conn):
    """
        Receives and decodes a JSON object using a 4-byte big-endian header.
    """
    header = recv_exact(conn, 4)
    size = int.from_bytes(header, "big")
    payload = recv_exact(conn, size)
    return json.loads(payload.decode("utf-8"))


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


def send_and_receive(host, port, obj):
    """
        High-level client utility to perform a synchronous request-response cycle.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        send_json(s, obj)
        reply = recv_json(s)
        return json.dumps(reply) + "\n"

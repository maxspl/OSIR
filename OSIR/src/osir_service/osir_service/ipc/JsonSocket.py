import json
import socket


def recv_exact(conn, num_bytes):
    buffer = b""
    while len(buffer) < num_bytes:
        chunk = conn.recv(num_bytes - len(buffer))
        if not chunk:
            raise ConnectionError("Socket closed")
        buffer += chunk
    return buffer

def recv_json(conn):
    header = recv_exact(conn, 4)
    size = int.from_bytes(header, "big")
    payload = recv_exact(conn, size)
    return json.loads(payload.decode("utf-8"))

def send_json(conn, obj, pydantic=False):
    if pydantic:
        data = obj.model_dump_json().encode("utf-8")
    else:
        data = json.dumps(obj).encode("utf-8")
    size = len(data).to_bytes(4, "big")
    conn.sendall(size + data)

# def send_and_receive(host, port, obj):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((host, port))

#         # 🔹 envoyer JSON
#         send_json(s, obj)

#         # 🔹 recevoir JSON
#         reply = recv_json(s)
#         print("Server replied:", reply)

def send_and_receive(host, port, obj):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        send_json(s, obj)
        reply = recv_json(s)
        return json.dumps(reply) + "\n" 
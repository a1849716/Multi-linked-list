import socket

host = "127.0.0.1"
port = input("input port used by server: ")
port = int(port)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    s.sendall(b"Hello, world")
    data = s.recv(1024)

print(f"Received {data!r}")
import sys
import socket
import selectors
import types
import threading

sel = selectors.DefaultSelector()

#search pattern 
search_pattern = sys.argv[4]

#set host and port and binding to socket
port = int(sys.argv[2])
ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssock.bind(('', port))

#entering listening mode
ssock.listen()
print(f"Listening on {(port)}")

#setting up non-blocking mode
ssock.setblocking(False)
sel.register(ssock, selectors.EVENT_READ, data=None)

# Function to handle each client connection
def client_handler(conn, addr):
    print(f"Connected by {addr}")
    try:
        with conn:
            while True:
                data = conn.recv(1024)  # Receive data from client
                if not data:
                    break  # Connection closed by the client
                print(f"Received from {addr}: {data.decode()}")
                conn.sendall(data)  # Echo the received data back to the client
    except Exception as e:
        print(f"Exception handling client {addr}: {e}")
    finally:
        print(f"Connection with {addr} closed")


# Event loop to accept new clients
def accept_wrapper(sock):
    conn, addr = sock.accept()  # Accept a new client connection
    print(f"Accepted connection from {addr}")
    conn.setblocking(True)  # Make the new client socket blocking
    # Start a new thread for the client handler
    threading.Thread(target=client_handler, args=(conn, addr), daemon=True).start()

# Event loop to listen for incoming connections
try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
except KeyboardInterrupt:
    print("Server shutting down")
finally:
    ssock.close()

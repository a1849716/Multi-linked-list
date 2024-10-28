import sys
import socket
import selectors
import time
import threading
from collections import defaultdict
from operator import itemgetter


#variable initiation
sel = selectors.DefaultSelector()
search_pattern = sys.argv[4]
shared_lock = threading.Lock()
shared_list = []
connection_counter = 0

#Classes for Node and Linked List
class Node:
    def __init__(self, line, book_id):
        self.line = line
        self.book_id = book_id
        self.next = None
        self.book_next = None

class linked_list:
    def __init__(self):
        self.head = None
        self.tail = None
        
    def add_node(self, line, book_id):
        new_node = Node(line, book_id)
        if self.head is None:
            self.head = new_node
        else:
            self.tail.next = new_node
        self.tail = new_node
        return new_node

# Function to add a node to the shared list in a thread-safe manner
def add_to_shared_list(node):
    with shared_lock:
        shared_list.append(node)  # Add the node to the shared list
        print(f"Node added to shared list: {node.line}")

# Function to handle each client connection
def client_handler(conn, addr, book_id, connection_number, search_word):
    print(f"Connected by {addr}")
    conn.setblocking(False)  # Set the connection to non-blocking mode
    buffer = ""  # Buffer to store incomplete data

    try:
        # Create a file for the client as soon as the connection is established
        file = open(f"book_{connection_number:02}.txt", 'w')  # Create and open file
        print(f"File book_{connection_number:02}.txt created for client {addr}")

        try:
            with conn:
                while True:
                    try:
                        data = conn.recv(1024)  # Try to receive data
                        if not data:
                            break  # No more data, close the connection

                        buffer += data.decode(errors='replace')  # Replaces undecodable characters with a placeholder (usually '?')

                        # Process complete lines
                        lines = buffer.split('\n')
                        buffer = lines.pop()  # Keep incomplete line in buffer

                        for line in lines:
                            if line.strip():  # Only process non-empty lines
                                # Check if the line contains the search word
                                if search_word in line:
                                    # Create a new node for each line and add it to shared_list
                                    new_node = Node(line, book_id)
                                    
                                    # Add to the shared list using shared_lock for thread-safety
                                    add_to_shared_list(new_node)
                                    
                                    # Write the filtered line directly to the file
                                    file.write(line + '\n')
                                    file.flush()  # Ensure the data is written immediately

                    except BlockingIOError:
                        continue  # No data available yet, continue waiting

        except Exception as e:
            print(f"Exception handling client {addr}: {e}")

    finally:
        file.close()  # Close the file when the connection ends
        print(f"Connection with {addr} closed and file book_{connection_number:02}.txt saved.")

def analysis_thread():
    while True:
        time.sleep(5)  # Analyze every 5 seconds
        pattern_count = defaultdict(int)
        
        with shared_lock:
            for node in shared_list:
                if search_pattern in node.line:
                    pattern_count[node.book_id] += 1
        
        # Output book titles sorted by pattern frequency
        if pattern_count:
            sorted_books = sorted(pattern_count.items(), key=itemgetter(1), reverse=True)
            print(f"\nPattern '{search_pattern}' Frequency Analysis:")
            for book_id, count in sorted_books:
                print(f"Book {book_id}: {count} occurrences")
        else:
            print(f"\nNo occurrences of pattern '{search_pattern}' found.")

def accept_wrapper(sock):
    global connection_counter
    conn, addr = sock.accept()  # Accept the new client connection
    print(f"Accepted connection from {addr}")

    # Increment connection_counter to assign unique connection_number
    connection_counter += 1
    connection_number = connection_counter
    book_id = connection_counter  # Here book_id is tied to connection_number

    conn.setblocking(True)  # Set the client socket to blocking mode

    # Start a new thread to handle the client, passing book_id, connection_number, and search_pattern
    threading.Thread(target=client_handler, args=(conn, addr, book_id, connection_number, search_pattern), daemon=True).start()

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

# Start analysis threads
threading.Thread(target=analysis_thread, daemon=True).start()

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
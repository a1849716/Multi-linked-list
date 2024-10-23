import sys
import socket
import selectors
import time
import threading
from collections import defaultdict

#variable initiation
sel = selectors.DefaultSelector()
search_pattern = sys.argv[4]
shared_lock = threading.Lock()
shared_list = []
book_count = 0

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

# Each book will have its own linked list.
books = {}



# Function to handle each client connection
def client_handler(conn, addr):
    global books_count
    print(f"Connected by {addr}")
    #incrases book_id and add to global linked list
    book_count += 1
    book_id = book_count
    books[book_id] = linked_list()
    try:
        with conn:
            while True:
                data = conn.recv(1024)  # Receive data from client
                if not data:
                    break  # Connection closed by the client
                
                buffer += data.decode()  # Append received data to buffer
                
                # Process complete lines
                lines = buffer.split('\n')
                buffer = lines.pop()  # Keep incomplete line in buffer
                    
                for line in lines:
                    # Add each line to the shared linked list
                    with shared_lock:
                        node = books[book_id].add_node(line, book_id)
                        shared_list.append(node)
                        print(f"Added node: {line}, Book ID: {book_id}")
    except Exception as e:
        print(f"Exception handling client {addr}: {e}")
    finally:
        # Write the book to a file when the connection closes
        filename = f"book_{book_id:02d}.txt"
        with open(filename, 'w') as f:
            current = books[book_id].head
            while current:
                f.write(current.line + "\n")
                current = current.book_next
        print(f"Connection with {addr} closed")



# Analysis thread to compute search pattern frequency
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
            sorted_books = sorted(pattern_count.items(), key=lambda x: x[1], reverse=True)
            print(f"\nPattern '{search_pattern}' Frequency Analysis:")
            for book_id, count in sorted_books:
                print(f"Book {book_id}: {count} occurrences")
        else:
            print(f"\nNo occurrences of pattern '{search_pattern}' found.")



# Event loop to accept new clients
def accept_wrapper(sock):
    conn, addr = sock.accept()  # Accept a new client connection
    print(f"Accepted connection from {addr}")
    conn.setblocking(True)  # Make the new client socket blocking
    # Start a new thread for the client handler
    threading.Thread(target=client_handler, args=(conn, addr), daemon=True).start()



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
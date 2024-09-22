import os
import socket
import selectors
import warnings

DEFAULT_PORT = 1256
MAX_PORT = 65535

def read_port_from_file(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

def validate_port(port_str):
    if port_str.isdigit():
        port = int(port_str)
        if 0 < port < MAX_PORT:
            return port
    warnings.warn("content port.info file is not valid")
    return None


def get_port():
    if os.path.exists('port.info'):
        content = read_port_from_file('port.info')
        port = validate_port(content)

        if port is None:
            return DEFAULT_PORT
        return port
    else:
        warnings.warn("file port.info is not exist")
        return DEFAULT_PORT

PORT = get_port()

sel = selectors.DefaultSelector()

def accept(sock, mask):
    try:
        conn, addr = sock.accept()  # Should be ready
        print('Accepted connection from', addr)
        conn.setblocking(False)
        sel.register(conn, selectors.EVENT_READ, read)
    except Exception as e:
        print(f"Error accepting connection: {e}")

def read(conn, mask):
    try:
        data = conn.recv(1024)  # Should be ready
        if data:
            print('Echoing', repr(data), 'to', conn)
            conn.send(data)  # Hope it won't block
        else:
            print('Closing', conn)
            sel.unregister(conn)
            conn.close()
    except Exception as e:
        print(f"Error reading data: {e}")
        sel.unregister(conn)
        conn.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.bind(("", PORT))
    print(f"Socket successfully bound to port {PORT}")
except socket.error as e:
    print(f"Failed to bind socket: {e}")
    exit(1)  # Exit the program if the socket cannot bind

sock.listen(100)  # Listen for incoming connections
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

print("Server is listening...")

try:
    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
except KeyboardInterrupt:
    print("Server is shutting down...")
finally:
    sel.close()
    sock.close()
    print("Server closed.")
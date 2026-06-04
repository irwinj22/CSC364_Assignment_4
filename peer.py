import sys
import socket
import threading

# list of files that peer has access to
local_files = []

# parse the command line
# returns the server and port
def parse_cl():
    if len(sys.argv) < 5:
        print("Error. Expect at least two arguments: host and port.")
        sys.exit(1)

    # grab host and port
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    peer_host = sys.argv[3]
    peer_port = int(sys.argv[4])

    # add local files
    for arg in sys.argv[3:]:
        local_files.append(arg)

    return (server_host, server_port, peer_host, peer_port)

# listen for connections from peers
def start_server(host, port):
    print("Start PEER server!")

    # start up as a socket, or something like that
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # allow reuse of socket after program terminates
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # bind to the server
        s.bind((host, port))
        s.listen(1)
    except Exception as e:
        print(f"[Server Error] Could not bind to port {port}: {e}")
        return

    while True:
        try:
            conn, addr = s.accept()
            print(f"Connected to client at {addr}")
            handler_thread = threading.Thread(target = handle_messages, args = (conn, addr), daemon=True)
            handler_thread.start()
        except: 
            print("Exception")
            break

    s.close()

def handle_messages(conn, addr):
    print(f"Server connected to peer: {addr}")

    while True:
        try:
            # TODO: want to act differently depend on the message type (offer, request, transfer, or ack)
            # which means that we are going to have to pack and then unpack the messages and stuff .. 
            data = conn.recv(1024)
            print(f"Received from {addr}: {data.decode('utf-8')}")
        except ConnectionResetError:
            print(f"\n[Server] Peer {addr} abruptly disconnected.")
            break

    conn.close()


# connects to peer and starts sending messages
# TODO: what is this process going to look like .. we are
# only going to know what 
def start_client(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        
        # send message
        message = "Hello, tracker server!"
        s.sendall(message.encode("utf-8"))

        # read the reply, i guess
        response = s.recv(1024)
        print(f"Message from server: {response.decode('utf-8')}")
    except socket.timeout:
        print("The connection attempt timed out.")

def main():
    server_host, server_port, peer_host, peer_port = parse_cl()

    # create thread to start server
    server_thread = threading.Thread(target = start_server, args = (peer_host, peer_port), daemon = True)
    server_thread.start()

    # then, on the client side, send a message to the tracker server (or something like that)
    client_thread = threading.Thread(target = start_client, args = (server_host, server_port), daemon = True)
    client_thread.start()

    # TOOD: replace this with client interface, or something
    server_thread.join()

    # cre


def log_files():
    print("------")
    print("logging files ..")
    for file in local_files:
        print(file)
    print("------ ")

if __name__ == "__main__":
    main()

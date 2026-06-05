import sys
import json
import time
import socket
import random
import threading
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

# list of local files (either from startup or grabbed from other peers)
local_files = []
# dicationary of all peers. key is peer_id and value is (host, port)
peer_id_addrs = {}
# all connections. key is (host, port) and value is socket
connections = {}
# all peers and their files. key is peer (through id) and value is list of all their files
peer_files = {}

# listen for connections from peers
def start_server(host, port, this_peer_id):
    print("Start Peer Server ...")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # allow reuse of socket after program terminates
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind to the server and listen
    try:
        s.bind((host, port))
        s.listen(1)
    except Exception as e:
        print(f"[Server Error] Could not bind to port {port}: {e}")
        return

    while True:
        try:
            # accept connection, spin up thread to handle communication
            conn, addr = s.accept()

            # send all offers immediately on new connection
            for file in local_files:
                print(f"[SEND OFFER] --> {addr} | file: {file}")
                payload = {
                    "message_type": "O",
                    "peer_id": this_peer_id,
                    "filename": file
                }
                conn.sendall(json.dumps(payload).encode('utf-8'))

            handler_thread = threading.Thread(target = handle_messages, args = (conn, addr, this_peer_id), daemon=True)
            handler_thread.start()
        except: 
            print("Exception")
            break

    s.close()

# handle incoming messages from peers
def handle_messages(conn, addr, this_peer_id):
    while True:
        try:
            data = conn.recv(1024)
            if not data: 
                break
            decoded_data = json.loads(data.decode('utf-8'))
            message_type = decoded_data.get("message_type")

            # handle different message types
            # offer 
            if message_type == "O":
                peer_id = decoded_data.get("peer_id")
                filename = decoded_data.get("filename")
                print(f"[RECV OFFER] <-- peer {peer_id} | file: {filename}")
                
                # add to internal log
                # TODO: does this make sense? 
                # what if there are multiple files? that means that I am going to get
                if peer_id not in peer_files:
                    peer_files[peer_id] = [filename]
                else: 
                    peer_files[peer_id].append(filename)
            # request
            elif message_type == "R":
                filename = decoded_data.get("filename")
                print(f"Recevied REQUEST for file: {filename}")
                # TODO ..
            elif message_type == "T":
                data = decoded_data.get("data")
                # TODO ...
            # ack
            elif message_type == "A":
                peer_id = decoded_data.get("peer_id")
                print(f"Recieved ACK from peer {peer_id}")

            # unknown type: error
            else:
                print(f"Error. Received unknown message type: {message_type}")
                sys.exit(1)
        except ConnectionResetError:
            print(f"\n[Server] Peer {addr} abruptly disconnected.")
            break

    conn.close()

# connects to tracker server and finds all known peers
def connect_tracker(server_host, server_port, client_host, client_port, this_peer_id):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server_host, server_port))

        # create and send payload with this peer's host and port
        payload = {
            "host": client_host,
            "port": client_port, 
            "peer_id" : this_peer_id
        }
        json_bytes = json.dumps(payload).encode('utf-8')
        s.sendall(json_bytes)

        # read the reply, which will contain all of the peers on the network
        response = s.recv(1024)
        response_peers = json.loads(response.decode('utf-8'))

        print("---")
        print("Peers in network:")
        if len(response_peers) == 0:
            print("No peers in network yet")
        else: 
            for other_peer_id, peer_info in response_peers.items():
                host = peer_info["host"]
                port = peer_info["port"]
                peer_id_addrs[other_peer_id] = (host, port)
                print(f"Peer {other_peer_id}: {host}, {port}")
        print("---")

    except socket.timeout:
        print("The connection attempt timed out.")

# parse the command line
# expects four arguments: tracker server host/port and this peer's host/port
# returns server host/port and this peer's host/port
def parse_cl():
    if len(sys.argv) < 5:
        print("Error. Expect at least four arguments: server host, server port, peer host, and peer port.")
        sys.exit(1)

    # grab hosts and ports
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    peer_host = sys.argv[3]
    peer_port = int(sys.argv[4])

    # add local files
    for arg in sys.argv[5:]:
        local_files.append(arg)

    return (server_host, server_port, peer_host, peer_port)

# connect directly to peer
# create socket, connect, and then start handler thread
def connect_to_peer(host, port, this_peer_id):
    if (host, port) not in connections:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        connections[(host, port)] = s
        handler_thread = threading.Thread(target=handle_messages, args=(s, (host, port), this_peer_id), daemon=True)
        handler_thread.start()

def main():
    server_host, server_port, peer_host, peer_port = parse_cl()

    # generate random peer_id
    this_peer_id = random.randint(0, 10000)

    # create thread to start server
    server_thread = threading.Thread(target = start_server, args = (peer_host, peer_port, this_peer_id), daemon = True)
    server_thread.start()

    # connect to the tracker server
    connect_tracker(server_host, server_port, peer_host, peer_port, this_peer_id)
    
    # first connect to all peers
    for peer, addr in peer_id_addrs.items():
        connect_to_peer(addr[0], addr[1], this_peer_id)

    # then send offers if we have any files
    for peer, addr in peer_id_addrs.items():
        send_all_offers(addr[0], addr[1], this_peer_id)

    session = PromptSession()

    # poll the user
    with patch_stdout():
        while True:
                # create prompt session
                user_message = session.prompt("> ")
                sys.stdout.flush()

                if user_message == "": 
                    print("Must enter non-empty message")
                    continue

                parse_user_message(user_message)

    # TODO: replace this with client interface, or something
    server_thread.join()

# parse user input
# to request file from other peer: -r <filename> <user>
# to print list of all peers and their files: -p
def parse_user_message(message):
    arguments = message.split()

    # request file from user
    if arguments[0] == "-r":
        if len(arguments) != 3:
            print(f"Error. Incorrect usage of -r. Expect 3 arguments and receieved {len(arguments)}")
            return

        print("I would make a request here ... ")
        # TODO: implement ...
    elif arguments[0] == "-p":
        if len(arguments) != 1:
            print(f"Error. Incorrect usage of -p. Expect 1 argument and receieved {len(arguments)}")
            return
        log_peer_files()
    else: 
        print(f"Error. Did not recognize command: {arguments[0]}")

# send offer for all files to peer
def send_all_offers(host, port, peer_id):
    for file in local_files:
        send_offer(host, port, peer_id, file)

# send single file offer to peer
def send_offer(host, port, peer_id, filename):
    print(f"[SEND OFFER] --> {host}:{port} | file: {filename}")
    s = connections[(host, port)]

    payload = {
            "message_type": "O",
            "peer_id" : peer_id,
            "filename": filename
    }
    s.sendall(json.dumps(payload).encode('utf-8'))

def log_peer_files():
    print("-------")
    print("All peers and files:")
    for peer_id, files in peer_files.items():
        addr = peer_id_addrs.get(str(peer_id), ("unknown", "unknown"))
        print(f"  peer {peer_id} | {addr[0]}:{addr[1]}")
        if not files:
            print(f"    no files")
        else:
            for file in files:
                print(f"    - {file}")
    print("-------")

if __name__ == "__main__":
    main()

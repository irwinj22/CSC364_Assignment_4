import sys
import json
import socket
import random
import threading
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

# list of local files (either from startup or transferred from other peers)
local_files = []
# dicationary of all peers. key is peer_id and value is dict: {'host' : host, 'port' : port}
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

            handler_thread = threading.Thread(target = handle_messages, args = (conn, addr), daemon=True)
            handler_thread.start()
        except: 
            print("Exception")
            break

    s.close()

# handle incoming messages from peers
def handle_messages(conn, addr):
    while True:
        try:
            data = conn.recv(1024)
            if not data: 
                break
            decoded_data = json.loads(data.decode('utf-8'))
            message_type = decoded_data.get("message_type")

            # offer 
            if message_type == "O":
                peer_id = decoded_data.get("peer_id")
                filename = decoded_data.get("filename")
                print(f"[RECV OFFER] <-- peer {peer_id} | file: {filename}")
                
                # store offer information
                if peer_id not in peer_files:
                    peer_files[peer_id] = [filename]
                else: 
                    peer_files[peer_id].append(filename)

            # request
            elif message_type == "R":
                filename = decoded_data.get("filename")
                print(f"[RECV REQUEST] -> peer {peer_id} | file: {filename}")

                transfer_file(conn, filename)

                # TODO .. do I just repond with the data to that? I am not quite sure really ..

            # transfer
            elif message_type == "T":
                data = decoded_data.get("data")
                print(f"[RECV TRANSFER]")

                # should open the file and write data

                # then, should broadcast to everyone that it has the file

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

# connect to tracker server and find all known peers
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

        # print and store
        print("---")
        print("Peers in network:")
        if len(response_peers) == 0:
            print("No peers in network yet")
        else: 
            for other_peer_id, peer_info in response_peers.items():
                host = peer_info["host"]
                port = peer_info["port"]
                peer_id_addrs[int(other_peer_id)] = {"host" : host, "port" : port}
                print(f"Peer {other_peer_id}: {host}, {port}")
        print("---")

    except socket.timeout:
        print("The connection attempt timed out.")

    tracker_thread = threading.Thread(target=handle_tracker_messages, args=(s, this_peer_id), daemon=True)
    tracker_thread.start()

# listen on the tracker socket for new_peer broadcasts 
# when new peer arrives, store, connect, and tell them about all of this peer's local files
def handle_tracker_messages(conn, this_peer_id):
    while True:
        data = conn.recv(1024)
        if not data:
            break
        decoded_data = json.loads(data.decode('utf-8'))
        # update something
        # TODO: create better comment, understand what's going on
        if decoded_data.get("message_type") == "new_peer":
            host = decoded_data.get("host")
            port = decoded_data.get("port")
            peer_id = decoded_data.get("peer_id")
            peer_id_addrs[int(peer_id)] = {"host" : host, "port" : port}
            connect_to_peer(host, port, this_peer_id)
            send_all_offers(host, port, this_peer_id)

# connect directly to peer
# create socket, connect, store, and then start handler thread
def connect_to_peer(host, port, this_peer_id):
    if (host, port) not in connections:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        connections[(host, port)] = s
        handler_thread = threading.Thread(target=handle_messages, args=(s, (host, port)), daemon=True)
        handler_thread.start()

# get socket from peer_id and filename
def get_socket(peer_id):
    # get host and port information
    if peer_id not in peer_id_addrs:
        print(f"Unknown peer {peer_id}")
        return 
    
    host = peer_id_addrs[peer_id].get('host')
    port = peer_id_addrs[peer_id].get('port')

    # get socket
    if (host, port) not in connections:
        print(f"No connection to peer {peer_id}")
        return
    
    return connections[(host, port)]


# make request to peer. i guess we are going to assume that the connection is open already?
def make_file_request(peer_id, filename):
    s = get_socket(peer_id)

    # send the information
    payload = {
        "message_type": "R",
        "filename": filename
    }
    s.sendall(json.dumps(payload).encode('utf-8'))
    print(f"[SEND REQUEST] -> peer {peer_id} | file: {filename}")

# transfer file data to peer.
# open the file break into chunks, and send. 
# complete transfer with acknowledgement message
def transfer_file(conn, filename):
    # open the file
    with open(filename, "rb") as f:
        while True:
            # read chunk
            chunk = f.read(1024)
            if not chunk:
                break  # File transmission complete

            # create payload
            payload = {
                "message_type": "T",
                "data": list(chunk), 
            }

            # send to connection
            print(f"[SEND TRANSFER] file: {filename}")
            conn.sendall(json.dumps(payload).encode('utf-8'))

# parse user input and handle accordingly
def parse_user_message(message):
    arguments = message.split()

    # request file from user
    if arguments[0] == "-r":
        if len(arguments) != 3:
            print(f"Error. Incorrect usage of -r. Expect 3 arguments and receieved {len(arguments)}")
            return
        
        try: 
            peer = int(arguments[1])
        except ValueError: 
            print("Error. Cannot convert argument to string. Did you enter everything in correct order?")
            return
        
        filename = arguments[2]

        # if peer exists and contains file, make request
        # otherwise, error
        if peer in peer_files and filename in peer_files[peer]:
            make_file_request(peer, filename)
        else: 
            print(f"Error. File {filename} does not exist in {peer}.")
            return
        
    # print all other peers and their files
    elif arguments[0] == "-p":
        if len(arguments) != 1:
            print(f"Error. Incorrect usage of -p. Expect 1 argument and receieved {len(arguments)}")
            return
        log_peer_files()

    # anything else: error
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

# log other peers and the files that they have
def log_peer_files():
    print("-------")
    print("All peers and files:")
    for peer_id, files in peer_files.items():
        addr = peer_id_addrs.get(peer_id)
        if addr is not None:
            print(f"  peer {peer_id} | {addr['host']}:{addr['port']}")
        # TODO: raise a better error here.
        else:
            print("COULD NOT FIND")
            return
        if not files:
            print(f"    no files")
        else:
            for file in files:
                print(f"    - {file}")
    print("-------")

# parse the command line
# expects four arguments: tracker server host/port and this peer's host/port
# returns server host/port and this peer's host/port
def parse_cl():
    if len(sys.argv) < 5:
        print("Error. Expect at least four arguments: server host, server port, peer host, and peer port.")
        sys.exit(1)

    # grab hosts and ports
    server_host = sys.argv[1]
    peer_host = sys.argv[3]
    try:
        server_port = int(sys.argv[2])
        peer_port = int(sys.argv[4])
    except ValueError: 
        print("Error. Cannot convert argument to string. Did you enter everything in correct order?")
        sys.exit(1)


    # add local files
    for arg in sys.argv[5:]:
        local_files.append(arg)

    return (server_host, server_port, peer_host, peer_port)

def main():
    server_host, server_port, peer_host, peer_port = parse_cl()

    # generate random peer_id
    this_peer_id = random.randint(0, 10000)

    # create thread to start server
    server_thread = threading.Thread(target = start_server, args = (peer_host, peer_port, this_peer_id), daemon = True)
    server_thread.start()

    # connect to the tracker server
    connect_tracker(server_host, server_port, peer_host, peer_port, this_peer_id)
    
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

if __name__ == "__main__":
    main()

import sys
import json
import socket
import threading

# key is id, value is another dictionary that contains host and port
all_peers = {}
# key is id, value is connections
peer_connections = {}  

# parse command line
# expect exactly two arguments: host and port
# returns the host and port
def parse_cl():
    if len(sys.argv) != 3:
        print("Error. Expect exactly two arguments: host and port.")
        sys.exit(1)

    # grab host and port
    host = sys.argv[1]
    port = int(sys.argv[2])

    return (host, port)

# receive message from new peer
# store that peer
# reply to that peer with all current peers
# then broadcast to existing peers that a new peer joined
def handle_peer(conn):
    try:
        data = conn.recv(1024)
        decoded_data = json.loads(data.decode('utf-8'))

        peer_host = decoded_data.get("host")
        peer_port = decoded_data.get("port")
        peer_id = decoded_data.get("peer_id")

        # reply with all current peers before adding the new one
        reply = json.dumps(all_peers)
        conn.sendall(reply.encode('utf-8'))

        # add new peer to our records
        all_peers[peer_id] = {"host": peer_host, "port": peer_port}
        peer_connections[peer_id] = conn

        # broadcast new peer to all existing peers
        broadcast = json.dumps({
            "message_type": "new_peer",
            "host": peer_host,
            "port": peer_port,
            "peer_id": peer_id
        }).encode('utf-8')

        for existing_peer_id, existing_conn in peer_connections.items():
            if existing_peer_id != peer_id:
                existing_conn.sendall(broadcast)

        print(f"Registered peer {peer_id}: {peer_host}:{peer_port}")
        log_peers()

    except Exception as e:
        print(f"Error handling peer: {e}")

# setup and start the server
def start_server(host, port):
    print("Start Tracker server ...")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind((host, port))
        s.listen(1)
    except Exception as e:
        print(f"[Server Error] Could not bind to port {port}: {e}")
        return
    
    # handle messages from new peers
    while True: 
        try:
            conn, addr = s.accept()
            handler_thread = threading.Thread(target=handle_peer, args=(conn,), daemon=True)
            handler_thread.start()
        except: 
            print("Exception")
            break

# log all existing peers
def log_peers():
    print("-------")
    print("Logging Peers")
    for peer_id, addr in all_peers.items():
        print(f"Peer {peer_id}: {addr['host']}, {addr['port']}")
    print("-------")

def main():
    host, port = parse_cl()
    start_server(host, port)

if __name__ == "__main__":
    main()
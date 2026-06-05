import sys
import json
import socket

# list of tuples (host, port)
# dictionary. key is id, value is another dictionary that contains host and port
all_peers = {}

# parse command line.
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

# start the server
def start_server(host, port):
    print("Start Tracker server ...")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((host, port))
        s.listen(1)
    except Exception as e:
        print(f"[Server Error] Could not bind to port {port}: {e}")
        return
    
    # receive messages from new peers
    while True: 
        try:
            # message from new peer containing host, port, and peer id
            conn, addr = s.accept()
            data = conn.recv(1024)
            decoded_data = json.loads(data.decode('utf-8'))
            
            # reply with all of the peers in the network
            reply = json.dumps(all_peers)
            json_bytes = reply.encode('utf-8')
            conn.sendall(json_bytes)

            # add the new peer (host and port) to list of peers
            peer_host = decoded_data.get("host")
            peer_port = decoded_data.get("port")
            peer_id = decoded_data.get("peer_id")
            all_peers[peer_id] = {"host" : peer_host,
                                  "port" : peer_port
                                  }
            
            print(f"Received connection from peer {peer_id}: {host}, {port}")

        except: 
            print("Exception")
            break
        log_peers()

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
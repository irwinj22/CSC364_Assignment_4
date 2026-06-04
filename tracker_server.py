# this is the tracker server .. we are going to want to spin up a server
# that keeps track of every peer in the network
# this will be used to tell new peers what's up and whatnot

import sys
import socket

# list of tuples (host, port)
all_peers = []

# parse command line.
# expect exactly two arguments: host and port
def parse_cl():
    if len(sys.argv) != 3:
        print("Error. Expect exactly two arguments: host and port.")
        sys.exit(1)

    # grab host and port
    host = sys.argv[1]
    port = int(sys.argv[2])

    return (host, port)

# start the server
# 
def start_server(host, port):
    print("Start TRACKER server!")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((host, port))
        s.listen(1)
    except Exception as e:
        print(f"[Server Error] Could not bind to port {port}: {e}")
        return
    
    # for now, receive message then send cool beans back
    while True: 
        try:
            #
            conn, addr = s.accept()
            print(f"Connected to client at {addr}")
            message = conn.recv(1024).decode("utf-8")
            print("Message: " + message)
            conn.sendall("cool beans".encode("utf-8"))
        except: 
            print("Exception")
            break

def main():
    host, port = parse_cl()
    start_server(host, port)
    print("hello")

if __name__ == "__main__":
    main()
## Startup
- step 1: boot up tracker server 
    - `python peer.py <server_host> <server_port>`
- step 2: register a peer
    - `python peer.py <server_host> <server_port> <peer_host> <peer_port> <list of local files>`

## User Interface
- to request file from other peer: -r <filename> <user>
- to print list of all peers and their files: -p
- TODO: to terminate peer: -e

## Progress
- currently:
    - tracker server setup, peers join and make themselves known to each other
    - user polling works, have to implement the file transfer stuff though
    - this involves both sending and receiving request, transfer, and ack things ...
- at that point, it's making sure that the network stays updated when files are exchanged
- and then handling errors and stuff like that


## Questions
- what if a peer wants to leave the network?
- eventually, peers should get an updated list of each other's files. how can i handle this? 
    - potential solution: send a broadcast as soon as you get something? 
- eventually: how to handle timeouts? 

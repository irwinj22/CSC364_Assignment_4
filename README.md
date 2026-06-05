## Startup
- step 1: boot up tracker server 
    - `python peer.py <server_host> <server_port>`
- step 2: register a peer
    - `python peer.py <server_host> <server_port> <peer_host> <peer_port> <list of local files>`

## User Interface
- to request file from other peer: -r `<filename>` `<user>`
- to print list of all peers and their files: -p
- TODO: to terminate peer: -e

## Progress
- currently:
    - tracker server setup, peers join and make themselves known to each other
    - user polling works, have to write data when a file is transferred
    - then, send the ack back
    - this involves both sending and receiving request, transfer, and ack things ...

- why can't the second peer send something to the first peer?

- possible fixes
    - periodic updates (how about every time a file is transferred?)
    - missing packets and retransmissions
    - file integrity check

- could easily do:
    - documentation: write what's going down in the README

## System Requirements / Limitations
- assumes that every peer has at least one file
- could redo with struct instead of json if i want to send multiple chunks of a file, i guess

- so now i am using json for the connection to the tracker server and struct for peer to peer communication

## Questions
- what if a peer wants to leave the network?
- eventually, peers should get an updated list of each other's files. how can i handle this? 
    - potential solution: send a broadcast as soon as you get something? 
- eventually: how to handle timeouts? 
- there is a connection from 1 to 2, but not from 2 to 1.
- why are all these errors occuring? i cannot figure how to get this assigmnent to work.

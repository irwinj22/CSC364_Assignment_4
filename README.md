## How to Run
- step 1: boot up tracker server 
    - `python peer.py <server_host> <server_port>`
- step 2: register a peer
    - `python peer.py <server_host> <server_port> <peer_host> <peer_port> <list of local files>`

and yeah should be good to go from there, i think ...

## Progress
- currently: tracker server starts, peers can send messages to it
- next steps: 
    - when peer joins, it should know who else is in network so that it can message them directly
    - the management from the server is what i don't quite understand yet, i guess ...
- peers should also send all of the files that they have stored
- figure out how 

## Questions
- so the actual process is that the peer would connect to a tracker server 
- then the tracker server responds with a list of peers
- at that point, the new peer can talk to whomever it wants to.
- what if a peer wants to leave the network?

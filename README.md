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

i think that my main question is how a new peer is supposed to find other peers? what messages are going to allow for that? 
does the tracker server send something to the new peer? i don't know ...

so those are the messages between peers, but it doesn't say anything about the server and the message
that the server can send to the client .. maybe it just sends a bunch of client ids or something like that? 

there should also be a randomly generated UUID or something for the peer, right? 

- ok so i could get the client to connect to other clients in the network, then it reaches out and sends a message
- but what from there? there should be some sort of user input, i guess. should the user be able to select who they are communicating with and stuff like that? 

- eventually, peers should get an updated list. how could i handle this? 

i think that i am just going to use json for creating all of the packets and structs and stuff like that

- eventually: how to handle timeouts? 

- what about that first peer .. how will people find out about their files? 
- should the tracker contain the files? 
- or do people need to update? 
- not sure what the best method would be here tbh ...

have to implement better logging and stuff but it is TECHNICALLY working, i think
just not the cleanest solution ever tbh ...
- make sure that you cannot enter duplicate ports
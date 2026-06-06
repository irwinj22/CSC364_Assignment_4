## Overview

Hello grader! This is my submission for Assignment 4. It is not complete but has several of the required components. 
Users are able to boot up a tracker server and then multiple peers. A client interface populates within each peer's terminal. The
interface allows peers to see the files that other peers have and request/transmit files.

## Commands
### Setup
- boot up tracker server: `python tracker_server.py <server_host> <server_port>`
- register a peer: `python peer.py <server_host> <server_port> <peer_host> <peer_port> <list of local files>`

### User Interface
- print list of all peers and their files: `-p`
- request file from other peer: `-r <filename> <user>`

## Example Usage
- step 1: boot up tracker server:
    - `python tracker_server.py localhost 5001`
- step 2: create peers:
    - `python tracker_server.py localhost 5001 localhost 5002 file1.txt`
    - `python tracker_server.py localhost 5001 localhost 5003 file2.txt`
- step 3: peer 1 looks up all other files
    -`p`
- step 4: peer 1 requests file2.txt from peer 2, where `<peer2>` is peer 2's randomly generated id
     - `-r file1.txt <user2>`

## Left Unfinished

These are the parts of the assignment that I have not finished:
    - periodic updates (how about every time a file is transferred?)
    - missing packets and retransmissions
    - file integrity check

## System Requirements / Limitations
- this implementation assumes that every peer has at least one file

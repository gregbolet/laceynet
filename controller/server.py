#!/usr/bin/env -S PYTHONPATH=../common python3

import socket
import pickle

from lacey import *
from _thread import *

from threading import Lock

# Array to hold state of all connected machines
# Maps device name to status
globalState = {}

# thread function
def handle_worker_request(conn):
    while True:

        # Blocking calls, max MSG_BUFF_SIZE bytes
        data = conn.recv(MSG_BUFF_SIZE)

        if not data:
            print('Client comm closed...', conn)
            break
        else:
            # Expecting a worker data packet
            workermsg = pickle.loads(data)

            if workermsg.request == WorkerMsg.HEARTBEAT:
                print('Got a heartbeat from:', conn)

            # Send the data back to the client, sends all bytes
            #conn.sendall(data)

    # close connection if no more data
    conn.close()
    return

def main():
    print("Hello from Controller!")

    # AF_INET is IPV4, SOCK_STREAM is for TCP protocol
    # Will automatically close connections
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Associate the given HOST with the given PORT
    s.bind((HOST, PORT))

    # Make this a listening server
    s.listen(MAX_CONNS)

    while True:
        # Block and wait for an incoming connection
        conn, addr = s.accept()

        print('Connected by', addr, socket.gethostbyaddr(addr[0])[0])

        start_new_thread(handle_worker_request, (conn,))

    # Close the socket
    s.close()
        

    return

main()

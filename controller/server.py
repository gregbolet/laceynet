#!/usr/bin/env -S PYTHONPATH=../common python3

import socket
import pickle

from lacey import *
from _thread import *
import Threading

print_lock = threading.lock()

# thread function
def handle_request(conn):
    while True:


        # Blocking calls, max MSG_BUFF_SIZE bytes
        data = conn.recv(MSG_BUFF_SIZE)

        if not data:
            print('No more data from client...', conn)
            break
        else:
            # Expecting a worker data packet
            workerData = pickle.loads(data)
            print(workerData.numbersToGuess)
            print(workerData.status)

            # Send the data back to the client, sends all bytes
            conn.sendall(data)

    # close connection if no more data
    c.close()
    return

def main():
    print("Hello from Controller!")

    # AF_INET is IPV4, SOCK_STREAM is for TCP protocol
    # Will automatically close connections
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Associate the given HOST with the given PORT
    s.bind((HOST, PORT))

    # Make this a listening server
    s.listen()

    while True:
        # Block and wait for an incoming connection
        conn, addr = s.accept()

        # Block until we have started the new thread
        print('Connected by', addr)
        print('AKA: ', socket.gethostbyaddr(addr[0]))

        start_new_thread(handle_request, (conn,))

    # Close the socket
    s.close()
        

    return

main()

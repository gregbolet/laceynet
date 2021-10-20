#!/usr/bin/env -S PYTHONPATH=../common python3

import socket
import pickle

from lacey import *

HOST = 'controller.laceynet'
PORT = 65432

def main():
    print("Hello from Controller!")

    # AF_INET is IPV4, SOCK_STREAM is for TCP protocol
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Associate the given HOST with the given PORT
        s.bind((HOST, PORT))

        # Make this a listening server
        s.listen()

        # Block and wait for an incoming connection
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            print('AKA: ', socket.gethostbyaddr(addr[0]))
            while True:
                # Blocking calls, max 4096 bytes
                data = conn.recv(4096)

                # If no bytes are received, connection is closed
                if not data:
                    break

                workerData = pickle.loads(data)
                print(workerData.numbersToGuess)
                print(workerData.status)

                # Send the data back to the client, sends all bytes
                conn.sendall(data)

    return

main()

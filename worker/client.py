#!/usr/bin/env -S PYTHONPATH=../common python3

import socket
import pickle

from lacey import *

HOST = 'controller.laceynet'
PORT = 65432

def main():
    print("Hello from Worker!")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # Create an object instance
        mydata = WorkerData()
        mydata.numbersToGuess = [3,4,5,6]
        mydata.status = 44

        # Pickle the object to send over the network
        tosend = pickle.dumps(mydata)

        # Send object to the server
        s.send(tosend)

        # Expect a message in return
        data = s.recv(4096)
        print('Received', repr(data))

    return

main()

#!/usr/bin/env -S PYTHONPATH=../common python3

import socket
import pickle

from lacey import *

def main():
    print("Hello from Worker!")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    # Create an object instance
    mydata = WorkerData()
    mydata.numbersToGuess = [3,4,5,6]
    mydata.status = 44

    while True:
        # Pickle the object to send over the network
        tosend = pickle.dumps(mydata)

        # Send object to the server
        s.send(tosend)

        # Expect a message in return
        data = s.recv(4096)
        print('Received', repr(data))

        # ask the client whether he wants to continue
        ans = input('\nDo you want to continue(y/n) :')
        if ans == 'y':
            continue
        else:
            break

    # Close the socket
    s.close()

    return

main()

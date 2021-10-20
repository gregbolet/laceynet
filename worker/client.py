#!/usr/bin/env -S PYTHONPATH=../common python3

import socket
import pickle

from lacey import *

lastHeartbeat = None

def sendMsg(s, obj):
    # Pickle the object to send over the network
    tosend = pickle.dumps(obj)

    s.send(tosend) 
    return

def sendHeartbeat(s):
    global lastHeartbeat
    lastHeartbeat = getCTS()
    beat = WorkerMsg(WorkerMsg.HEARTBEAT)
    sendMsg(s, beat)
    print('Sent heartbeat!', lastHeartbeat)
    return

def registerWorker(s):
    regReq = WorkerMsg(WorkerMsg.REGISTER)
    sendMsg(s, regReq)

    # Expecting a confirmation back
    return


def main():
    global lastHeartbeat
    print("Hello from Worker!")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    #registerWorker(s)

    while True:

        # Check if we need to send a heartbeat
        shouldSendBeat = (lastHeartbeat == None) or (getTSDiff(getCTS(), lastHeartbeat) > HEARTBEAT_INTERVAL)

        print(shouldSendBeat)

        if shouldSendBeat:
            sendHeartbeat(s)
            

    # Close the socket connection
    s.close()

    return

main()

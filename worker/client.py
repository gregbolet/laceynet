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
    lastHeartbeat = getCTS()
    beat = WorkerMsg(WorkerMsg.HEARTBEAT)
    sendMsg(s, beat)
    print('Sent heartbeat!', lastHeartbeat)
    return

def registerWorker(s):
    regReq = WorkerMsg(WorkerMsg.REGISTER)
    sendMsg(s, regReq)
    return


def main():
    print("Hello from Worker!")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    # Create an object instance
    mydata = WorkerMsg()
    mydata.request = 1

    while True:

        # Get the current timestamp
        shouldSendBeat = (getTSDiff(getCTS(), lastHeartbeat) > HEARTBEAT_INTERVAL)

        if lastHeartbeat == None or shouldSendBeat:
            sendHeartbeat()
            

    # Close the socket connection
    s.close()

    return

main()

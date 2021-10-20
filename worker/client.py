#!/usr/bin/env -S PYTHONPATH=../common python3

from lacey import *

lastHeartbeat = None


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
    conf = s.recv(MSG_BUFF_SIZE)
    
    # return a ControllerMsg object
    return pickle.loads(conf)


def main():
    global lastHeartbeat
    print("Hello from Worker!")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    
    # register ourselves with the server
    cntrlMsg = registerWorker(s)
    if cntrlMsg.response is not ControllerMsg.REGIST_SUCC:
        print('Could not get registered to controller!')
        return
    else:
        print('Succesfully Registered!')
        

    while True:

        # Check if we need to send a heartbeat
        shouldSendBeat = (lastHeartbeat == None) or (getTSDiff(getCTS(), lastHeartbeat) > HEARTBEAT_INTERVAL)

        if shouldSendBeat:
            sendHeartbeat(s)
            

    # Close the socket connection
    s.close()

    return

# Always keep trying to connect and register worker to controller
while True:
    main()

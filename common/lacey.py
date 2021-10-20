#!/usr/bin/env python3

import datetime

# Maximum message buffer size
MSG_BUFF_SIZE = 4096

# The server's hostname -- resovled later via DNS
HOST = 'controller.laceynet'

# Port to communicate on
PORT = 65432

# The maximum number of connections allowed until
# the server starts rejecting requests
MAX_CONNS = 40

# This is how many seconds the client should wait
# before sending a heartbeat, we expect to wait 10 seconds
HEARTBEAT_INTERVAL = 10

# Get the current timestamp
def getCTS():
    return datetime.datetime.now().timestamp()

# Check the difference of two timestamps
# returns the diff in seconds
def getTSDiff(ts1, ts2):
    if ts1 > ts2:
        diff = ts1 - ts2
    else:
        diff = ts2 - ts1
    return diff.total_seconds()


# This object will allow the server to keep track of 
# the state of an individual worker
class WorkerState:
    
    # 0 = joined game 
    # 1 = no heartbeat for last 30 seconds
    workerStatus = 0

    # Timestamp of last time this worker sent a heartbeat
    lastHeartbeat = None

# These are the requests the workers/client can send
class WorkerMsg:

    # Static vars to describe messages
    HEARTBEAT = 1
    REGISTER = 2

    # 0 = get game status
    # 1 = is heartbeat msg
    # 2 = register to join game
    # 3 = been touched by stylus

    # Keep track of when this message was sent
    self.timestamp = None

    def __init__(self, requestCode):
        self.request = requestCode
        self.timestamp = datetime.datetime.now().timestamp()

# These are the messages the server sends to the clients
class ControllerMsg:

    # The list of numbers this worker will be "guessing"
    numbersToGuess = []

    # Let the device know what the game state is
    # 0 = wait for start signal
    # 1 = game started
    # 2 = game paused
    # 3 = game ended
    # 4 = succesfully registered worker
    gameState = 0



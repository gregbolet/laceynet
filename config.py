#!/usr/bin/env python3

import datetime
import socket
import pickle
import time
from threading import Lock

# Maximum message buffer size
MSG_BUFF_SIZE = 1024

# The server's hostname -- resovled later via DNS
HOST = 'controller.laceynet'
# HOST = '127.0.0.1'

# Port to communicate on
PORT = 65432
# PORT = 5000

# The maximum number of connections allowed until
# the server starts rejecting requests
MAX_CONNS = 40

# This is how many seconds the client should wait
# before sending a heartbeat, we expect to wait 10 seconds
HEARTBEAT_INTERVAL = 10 #2

# If after 20 seconds we don't get a heartbeat, consider
# the node disconnected
HEARTBEAT_TIMEOUT = 20


def get_alias_from_conn(conn):
    return socket.gethostbyaddr(conn.getpeername()[0])[0]


# Sends an object over the socket s
def send_msg(s, obj):
    # Pickle the object to send over the network
    print("sending: {}".format(obj))
    tosend = pickle.dumps(obj)
    s.send(tosend)


# Get the current timestamp
def get_cts():
    return datetime.datetime.now().timestamp()


# Check the difference of two timestamps
# returns the diff in seconds
def get_ts_diff(ts1, ts2):
    if ts1 > ts2:
        diff = ts1 - ts2
    else:
        diff = ts2 - ts1
    return diff


# This object will allow the server to keep track of 
# the state of an individual worker
# TODO: not being used at the moment
class WorkerState:

    NOT_REGISTERED = 0
    REGISTERED = 1
    PLAYING = 2
    
    def __init__(self):
        self.status = self.NOT_REGISTERED
        self.last_heartbeat = None

    def tick_heartbeat(self):
        self.last_heartbeat = get_cts()
        
    def is_alive(self):
        time_since_last_beat = get_ts_diff(get_cts(), self.lastHeartbeat)
        return (time_since_last_beat < HEARTBEAT_TIMEOUT)


# These are the requests the workers/client can send
class WorkerMsg:

    # Static vars to describe messages
    HEARTBEAT = 1
    REGISTER = 2
    IWON = 3
    
    def __init__(self, request_code):
        self.request = request_code
        self.timestamp = get_cts() 

    def __str__(self):
        message = "worker sent {}".format(WorkerMsg(self.request))
        return message


# These are the messages the server sends to the clients
class ControllerMsg:

    # Let the device know what the game state is
    # these are response codes
    CONTINUE = 2
    GAME_RESTART = 3
    REGIST_SUCC = 4
    REGIST_FAIL = 5

    def __init__(self, response_code):
        self.response = response_code
        self.timestamp = get_cts() 

        # The list of numbers this worker will be "guessing"
        self.numbers_to_guess = []
        self.winning_num = -1

    def __str__(self):
        message = "server is sending {} with numbers to guess as {}".format(ControllerMsg(self.response), self.numbers_to_guess)
        return message


# Override the print function to show timestamps
import builtins as __builtin__
def print(*args, **kwargs):
    __builtin__.print("[%s] " % str((datetime.datetime.now())), end='')
    return __builtin__.print(*args, **kwargs)


class AtomicInt:
    def __init__(self, val):
        self.__datalock = Lock()
        self.__val = val
        return

    def lock(self):
        self.__datalock.acquire()
        return

    def unlock(self):
        self.__datalock.release()
        return

    def get_int(self):
        toret = self.__val
        return toret 

    def set_int(self, val):
        self.__val = val
        return
        

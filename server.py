#!/usr/bin/env -S PYTHONPATH=../common python3

from sys import platform
from lacey import *
from _thread import *
from guessingGame import guessingGame
from threading import Lock

def restartAllWorkers():
    global connList
    global game
    for alias in connList:
        conn = connList[alias]
        msg = ControllerMsg(ControllerMsg.GAME_RESTART)
        msg.numbersToGuess = game.getGuessesForAlias(alias)
        msg.winningNum = game.getWinGuess()
        sendMsg(conn, msg)

    return



# thread function
def handle_worker_request(conn):
    global game
    while True:

        # Blocking calls, max MSG_BUFF_SIZE bytes
        data = conn.recv(MSG_BUFF_SIZE)
        alias = getAliasFromConn(conn)

        if not data:
            print('Connection to [', alias, '] closed...', sep='')
            break
        else:
            # Expecting a worker data packet
            workermsg = pickle.loads(data)

            if workermsg.request == WorkerMsg.HEARTBEAT:
                print('Heartbeat from:', alias)
            elif workermsg.request == WorkerMsg.REGISTER:
                print('Registration request from:', alias)
                game.addNewPlayer(alias)
                cntrlMsg = ControllerMsg(ControllerMsg.REGIST_SUCC)
                cntrlMsg.numbersToGuess = [1,2,3,4,6,7,8,9,10,5]#game.getGuessesForAlias(alias)
                cntrlMsg.winningNum = 5#game.getWinGuess()
                sendMsg(conn, cntrlMsg) 

            # Send the data back to the client, sends all bytes
            #conn.sendall(data)

    # close connection if no more data
    conn.close()
    return

def main():
    global game
    global connList

    try:
        print("Controller Starting...")

        # AF_INET is IPV4, SOCK_STREAM is for TCP protocol
        # Will automatically close connections
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Associate the given HOST with the given PORT
        s.bind((HOST, PORT))

        # Make this a listening server
        s.listen(MAX_CONNS)

        # Create a new guessing game
        game = guessingGame(10)

        # Keep track of the connections
        connList = {}

        print("Socket server ready!")

        while True:
            # Block and wait for an incoming connection
            conn, addr = s.accept()

            alias = getAliasFromConn(conn)
            print('Connected by:', alias)

            # Keep track of the new connection
            connList[alias] = conn

            start_new_thread(handle_worker_request, (conn,))

    finally:
        # Close the socket
        s.close()

    return

main()

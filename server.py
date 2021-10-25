#!/usr/bin/env -S PYTHONPATH=../common python3

from sys import platform
from lacey import *
from _thread import *
from guessingGame import guessingGame
from threading import Lock

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
                cntrlMsg.numbersToGuess = game.getGuessesForAlias(alias)
                cntrlMsg.winningNum = game.getWinGuess()
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
        #connList
    
        print("Socket server ready!")
    
        while True:
            # Block and wait for an incoming connection
            conn, addr = s.accept()
    
            print('Connected by:', getAliasFromConn(conn))
    
            start_new_thread(handle_worker_request, (conn,))
    
    finally:
        # Close the socket
        s.close()

    return

main()

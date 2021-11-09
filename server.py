#!/usr/bin/env -S PYTHONPATH=../common python3

from sys import platform
from config import *
from _thread import *
from guessingGame import guessingGame
from threading import Lock


def restart_all_workers():
    global game
    global conn_list
    global conn_lock

    game.restartGame()
    for alias in conn_list:
        conn = conn_list[alias]
        msg = ControllerMsg(ControllerMsg.GAME_RESTART)
        msg.numbersToGuess = game.getGuessesForAlias(alias)
        msg.winningNum = game.getWinGuess()
        sendMsg(conn, msg)
        print('Restarted:', alias)


# thread function to handle worker connection
def handle_worker_conn(conn):
    global game
    global conn_list
    global conn_lock
    global restart

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

            # if received a hearbeat message
            if workermsg.request == WorkerMsg.HEARTBEAT:
                print('Heartbeat from:', alias)
                cntrlMsg = ControllerMsg(ControllerMsg.CONTINUE)
                sendMsg(conn, cntrlMsg) 

            elif workermsg.request == WorkerMsg.REGISTER:
                print('Registration request from:', alias)
                game.addNewPlayer(alias)
                restart_all_workers()

            elif workermsg.request == WorkerMsg.IWON:
                print('We have a winner! -- Restarting game')
                restart_all_workers()

    # close connection if no more data
    conn.close()


def main():
    global game
    global conn_list
    global conn_lock

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

        # Set up empty connection list
        conn_list = {}

        # initialize the lock
        conn_lock = Lock()
        print("Socket server ready!")

        while True:
            # Block and wait for an incoming connection
            conn, addr = s.accept()

            # receives a new connection
            alias = getAliasFromConn(conn)
            print('Connected by:', alias)

            # start a new connection thread
            start_new_thread(handle_worker_conn, (conn,))
            # Keep track of the new connection
            conn_lock.acquire()
            conn_list[alias] = conn
            conn_lock.release()

    finally:
        # Close the socket
        s.close()


main()
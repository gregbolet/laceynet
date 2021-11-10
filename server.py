#!/usr/bin/env -S PYTHONPATH=../common python3

from config import *
from guessingGame import GuessingGame
from threading import Lock, Thread


def restart_all_workers():
    global game
    global conn_list
    global conn_lock

    game.restart_game()
    for alias in conn_list:

        conn_lock.acquire()
        conn = conn_list[alias]
        conn_lock.release()

        msg = ControllerMsg(ControllerMsg.GAME_RESTART)
        msg.numbers_to_guess = game.get_guesses_for_alias(alias)
        msg.winning_num = game.get_win_guess()
        send_msg(conn, msg)
        print('Restarted:', alias)

class ConnectionThread:
    def __init__(self):
        print('Init connection thread!')

    # thread function to handle worker connection
    def __handle_worker_conn(self):
        global game
        global conn_list
        global conn_lock
        global conn

        last_time_heartbeat = get_cts()

        while True:
            # Blocking calls, max MSG_BUFF_SIZE bytes
            data = conn.recv(MSG_BUFF_SIZE)
            alias = get_alias_from_conn(conn)

            if not data: # if there's no data being sent to server from client
                print('Connection to [', alias, '] closed...', sep='')
                break
            else:
                # Expecting a worker data packet
                workermsg = pickle.loads(data)

                # if received a hearbeat message
                if workermsg.request == WorkerMsg.HEARTBEAT:
                    print('Heartbeat from:', alias)
                    cntrl_msg = ControllerMsg(ControllerMsg.CONTINUE)
                    last_time_heartbeat = get_cts()
                    send_msg(conn, cntrl_msg) 

                # handles when a worker registers (joined the game)
                elif workermsg.request == WorkerMsg.REGISTER:
                    print('Registration request from:', alias)
                    game.add_new_player(alias)
                    restart_all_workers()

                # handles if a worker won the game
                elif workermsg.request == WorkerMsg.IWON:
                    print('We have a winner! -- Restarting game')
                    restart_all_workers()

                if get_ts_diff(get_cts(), last_time_heartbeat) > HEARTBEAT_TIMEOUT:
                    break
        # close connection if no more data
        conn.close()

    # This is what the threading.Thread.start will call 
    def __call__(self, *args, **kwargs):
        global conn
        print("Forked connection thread")
        self.__handle_worker_conn()
        while True:
            continue


def main():
    global game
    global conn_list
    global conn_lock
    global conn

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
        game = GuessingGame(10)

        # Set up empty connection list
        conn_list = {}

        # initialize the lock
        conn_lock = Lock()
        print("Socket server ready!")

        while True:
            # Block and wait for an incoming connection
            conn, addr = s.accept()

            # receives a new connection
            alias = get_alias_from_conn(conn)
            print('Connected by:', alias)

            # keep track of the new connection
            conn_lock.acquire()
            conn_list[alias] = conn
            conn_lock.release()

            # start a new connection thread
            connection_thread = Thread(target=ConnectionThread())
            connection_thread.start()

    finally:
        # Close the socket
        s.close()


main()
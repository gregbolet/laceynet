#!/usr/bin/env -S PYTHONPATH=../common python3

from config import *
from guessingGame import GuessingGame
from threading import Lock, Thread
import select

game = None
conn_list = []
conn_lock = None
ready_flag = AtomicInt(0)
target_time = -1
time_lock = None

def restart_all_workers():
    global game
    global conn_list
    global conn_lock

    game.restart_game()
    for alias in conn_list:
        conn_lock.acquire()
        player = conn_list[alias]
        print("I'm starting the game!!")
        print("connlist: {}".format(player))
        conn_lock.release()

        msg = ControllerMsg(ControllerMsg.GAME_START)
        print("number I'm sending: {}".format(game.get_guesses_for_alias(alias)))
        msg.numbers_to_guess = game.get_guesses_for_alias(alias)
        msg.winning_num = game.get_win_guess()
        send_msg(player, msg)
        print('Restarted:', alias)


class ConnectionThread:
    def __init__(self):
        print('Init connection thread!')

    # This is what the threading.Thread.start will call 
    def __call__(self, *args, **kwargs):
        global game
        global conn_list
        global conn_lock
        global target_time
        global time_lock

        conn = args[0]
        print("Forked connection thread")
        last_time_heartbeat = get_cts()

        while True:

            ready_flag.lock()
            if ready_flag.get_int() == 0:
                check_if_time_up()
            ready_flag.unlock()
            ready = select.select([conn], [], [], 0.5) # wait for 5 sec to see if there's data received
            if ready[0]: # only read when there's data available
            # Blocking calls, max MSG_BUFF_SIZE bytes
            # only ack if received anything 
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
                        # send continue signal
                        cntrl_msg = ControllerMsg(ControllerMsg.CONTINUE)
                        last_time_heartbeat = get_cts()
                        send_msg(conn, cntrl_msg)

                    # handles when a worker registers (joined the game)
                    elif workermsg.request == WorkerMsg.REGISTER:
                        print('Registration request from:', alias)
                        game.add_new_player(alias)

                        cntrl_msg = ControllerMsg(ControllerMsg.REGIST_SUCC)
                        send_msg(conn, cntrl_msg)
                        # restart the timer
                        time_lock.acquire()
                        target_time = get_cts()
                        print("updated target time to be {}".format(target_time))
                        time_lock.release()
                        # restart_all_workers()

                    # handles if a worker won the game
                    elif workermsg.request == WorkerMsg.IWON:
                        print('We have a winner! -- Restarting game')
                        ready_flag.lock()
                        ready_flag.set_int(0) # not ready
                        ready_flag.unlock()

                        time_lock.acquire()
                        target_time = -1 # reset the waiting room timer
                        time_lock.acquire()
                        # restart_all_workers()


                if get_ts_diff(get_cts(), last_time_heartbeat) > HEARTBEAT_TIMEOUT:
                    break

        # close connection if no more data
        conn.close()


def check_if_time_up():
    global time_lock
    global target_time
    global ready_flag

    res = False 
    # check if is time to start the game
    # ready_flag.lock()
    time_lock.acquire()
    # if waiting room is open and the timer is up
    if get_ts_diff(get_cts(), target_time) > WAITING_ROOM_TIMER:
        # time_lock.release()
        # ready_flag.unlock()
        # start the game!
        ready_flag.set_int(1)
        restart_all_workers()
        res = True
    else:
        print("I'm checking waiting room timer")
    time_lock.release()
    # ready_flag.unlock()
    return res


def main():
    global game
    global conn_list
    global conn_lock
    global time_lock
    global target_time

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
        time_lock = Lock()
        print("Socket server ready!")

        time_lock.acquire()
        target_time = get_cts()
        time_lock.release()

        while True:
            # Block and wait for an incoming connection
            conn, addr = s.accept()

            # ready = select.select([conn], [], [], 0.5) # wait for 5 sec to see if there's data received
            # if ready[0]: # only read when there's data available
                # receives a new connection
            alias = get_alias_from_conn(conn)
            print('Connected by:', alias)
            
            # if check_if_time_up():
            #     continue

            ready_flag.lock()
            if ready_flag.get_int() == 0: # if still adding players
                # ready_flag.unlock()
                # keep track of the new connection
                conn_lock.acquire()
                conn_list[alias] = conn
                conn_lock.release()

                # start a new connection thread
                connection_thread = Thread(target=ConnectionThread(), args=(conn,))
                connection_thread.start()
            else:
                print("{} missed the game :(".format(alias))
                cntrl_msg = ControllerMsg(ControllerMsg.REGIST_FAIL)
                send_msg(conn, cntrl_msg)
            ready_flag.unlock()
            
            # check_if_time_up()

    finally:
        # Close the socket
        s.close()


main()
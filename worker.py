from config import *
from threading import Lock, Thread


conn = None
nums = []
winNum = -1
restartFlag = AtomicInt(0)
isRegFlag = AtomicInt(0)
globalDataLock = Lock()

class SenderThread:
    def __init__(self):
        print('Init sender thread!')
        return

    def __register_worker(self):
        global conn
        regReq = WorkerMsg(WorkerMsg.REGISTER)
        send_msg(conn, regReq)
        print('Sent registration request!')
        return

    def __sendHeartbeat(self):
        global conn
        beat = WorkerMsg(WorkerMsg.HEARTBEAT)
        send_msg(conn, beat)
        self.lastHeartbeat = get_cts()
        print('Sent heartbeat!')
        return

    # This is what the threading.Thread.start will call 
    def __call__(self, *args, **kwargs):
        global conn
        global nums
        global winNum
        global globalDataLock
        print("Forked sender thread")

        # Get ourselves registered
        self.__register_worker()
        while True:
            winNum = winNum
        return

class RecvThread:
    def __init__(self):
        print('Init receiving thread!')
        return

    # This is what the threading.Thread.start will call 
    def __call__(self, *args, **kwargs):
        global conn
        global nums
        global winNum
        global globalDataLock
        global isRegFlag
        print("Forked recv thread")

        # Handle restart/continue requests
        while True:
            # Expecting a confirmation back
            conf = conn.recv(MSG_BUFF_SIZE)
            print('Got a server response!')

            # return a ControllerMsg object
            resp = pickle.loads(conf)
            print('Unpickled response object!')

            if resp.response is ControllerMsg.CONTINUE:
                print('Continuing game...')

            elif resp.response is ControllerMsg.REGIST_SUCC:
                print('Registration succesfull...')
                isRegFlag.lock()
                isRegFlag.set_int(1)
                isRegFlag.unlock()

            elif resp.response is ControllerMsg.GAME_RESTART:
                globalDataLock.acquire()
                restartFlag.lock()
                restartFlag.set_int(1)

                nums = resp.numbers_to_guess
                winNum = resp.winning_num
                print('Got new restart data: ', nums)

                globalDataLock.release()
                restartFlag.unlock()

        return

def setupGUI():
    # Setup the GUI object and return it
    guiobj = None
    return guiobj

def main():
    global conn
    global nums
    global winNum
    global globalDataLock
    
    print('Starting worker!')
    print('Establishing Connection...')

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((HOST, PORT))

    print('Connection READY!')

    recvThread   = Thread(target = RecvThread())
    senderThread = Thread(target = SenderThread())

    # Tell the threads to start running
    senderThread.start()
    recvThread.start()

    print('Sender + Receiver Threads Started')
    print('Setting up GUI...')

    setupGUI()

    print('GUI set up')

    # Now we loop waiting for a restart game signal
    while True:
        restartGameLock.acquire()

        restartGameLock.release()

    print('Worker done')
    return


main()
from config import *
from threading import Lock, Thread


conn = None
nums = []
winNum = -1
restartGameFlag = 0
globalDataLock = Lock()
restartGameLock = Lock()

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
        print("Forked recv thread")

        # Handle restart/continue requests
        while True:
            # Expecting a confirmation back
            globalDataLock.acquire()
            conf = conn.recv(MSG_BUFF_SIZE)
            globalDataLock.release()
            print('Got a server response!')

            # return a ControllerMsg object
            resp = pickle.loads(conf)
            print('Unpickled response object!')

            if resp.response is ControllerMsg.CONTINUE:
                print('Continuing game...')
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
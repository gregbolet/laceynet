import config
from threading import Lock, Thread
import sys, random


conn = None
nums = []
winNum = -1
globalDataLock = Lock()


class SenderThread:
    def __init__(self):
        print('Init sender thread!')
        return

    # This is what the threading.Thread.start will call 
    def __call__(self, *args, **kwargs):
        print("Forked sender thread")
        return

class RecvThread:
    def __init__(self):
        print('Init receiving thread!')
        return

    # This is what the threading.Thread.start will call 
    def __call__(self, *args, **kwargs):
        print("Forked recv thread")
        return



def main():
    print('Starting worker!')

    recvThread   = Thread(target = RecvThread())
    senderThread = Thread(target = SenderThread())

    # Tell the threads to start running
    senderThread.start()
    recvThread.start()

    print('Worker done')
    return


main()
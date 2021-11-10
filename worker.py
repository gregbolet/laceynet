from config import *
from threading import Lock, Thread
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys, random


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

class GameWindow(QMainWindow):
    def __init__(self,callback,setFun):
        super().__init_()
        self.player = callback
        self.setWindowTitle("Blockchain")
        self.UIComponents(self.player)
        setFun(self.button)
        self.showFullScreen()
        self.setUIGeometries()

    def setUIGeometries(self):
        buttonWidth = 1000
        buttonHeight = 1000
        self.button.setGeometry(self.width()//2-buttonWidth//2, self.height()//2-buttonHeight//2,buttonWidth,buttonHeight)

    def UIComponents(self):
        self.button = QPushButton("Connecting...",self)
        self.exitButton = QPushButton("EXIT", self)
        self.button.setFont(QFont('Times', 45))
        self.button.clicked.connect(self.player)
        self.exitButton.clicked.connect(self.exit)

    def exit(self):
        sys.exit(App.exec())

    def setWinnerStyle(self):
        self.button.setText("Winner!")
        self.button.setStyleSheet("background-color: yellow")
        self.button.setEnabled(False)
        self.button.repaint()

    def setButtonText(self, text):
        self.button.setText(text)

    def getButton(self):
        return self.button

def buttonCallback(self):
    print('callback')
    globalDataLock.acquire()
    if len(nums) > 0:
        if self.restart



def setButton(self,button):
    self.button = button

def setupGUI(self):
    # Setup the GUI object and return it
    App = QApplication(sys.argv)
    window = GameWindow(buttonCallback,setButton)
    guiobj = window #returns the window
    return guiobj



def main(self):
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


    self.guiobj = setupGUI()

    print('GUI set up')

    # Now we loop waiting for a restart game signal
    while True:
        restartGameLock.acquire()

        restartGameLock.release()

    print('Worker done')
    return


main()
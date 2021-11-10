from config import *
from threading import Lock, Thread
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys, random

conn = None
nums = []
winNum = -1
currIdx = -1
restartFlag = AtomicInt(0)
iWonFlag = AtomicInt(0)
#isRegFlag = AtomicInt(0)
globalDataLock = Lock()
guiobj = None
App = None

def checkIfWon():
    global iWonFlag
    iWonFlag.lock()
    if iWonFlag.get_int() == 1:
        iWonFlag.unlock()
        return True
    iWonFlag.unlock()
    return False

class SenderThread:
    def __init__(self):
        print('Init sender thread!')
        self.lastHeartbeat = None
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

    def doHeartbeat(self):
        # Check if we need to send a heartbeat
        shouldSendBeat = (self.lastHeartbeat == None) or (get_ts_diff(get_cts(), self.lastHeartbeat) > HEARTBEAT_INTERVAL)

        if shouldSendBeat:
            self.__sendHeartbeat()

        return

    # This is what the threading.Thread.start will call 
    def __call__(self, *args, **kwargs):
        global conn
        print("Forked sender thread")

        # Get ourselves registered
        self.__register_worker()

        while True:
            self.doHeartbeat()

            if checkIfWon():
                winnermsg = WorkerMsg(WorkerMsg.IWON)
                send_msg(conn, winnermsg)

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
        #global isRegFlag
        global iWonFlag
        global currIdx
        global restartFlag
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

            elif resp.response is ControllerMsg.GAME_RESTART:
                print('Restarting game...')
                #globalDataLock.acquire()
                #restartFlag.lock()
                #iWonFlag.lock()
                restartFlag.set_int(1)
                iWonFlag.set_int(0)

                nums = resp.numbers_to_guess
                winNum = resp.winning_num
                # Start at one index behind
                currIdx = -1
                print('Got new restart data: numbers', nums)
                print('Got new restart data: winNum ', winNum)

                #globalDataLock.release()
                #restartFlag.unlock()
                #iWonFlag.unlock()

        return

class GameWindow(QMainWindow):
    def __init__(self,callback):
        super().__init__()
        self.buttonCallback = callback
        self.setWindowTitle("Blockchain")
        self.UIComponents()
        print('Setup UI components!')
        self.showFullScreen()
        print('made fullscreen!')
        self.setUIGeometries()
        print('set geometries!')
        return

    def setUIGeometries(self):
        buttonWidth = 1000
        buttonHeight = 1000
        self.button.setGeometry(self.width()//2-buttonWidth//2, self.height()//2-buttonHeight//2,buttonWidth,buttonHeight)
        self.exitButton.setGeometry(100,100,250,250)
        return

    def UIComponents(self):
        self.button = QPushButton("Connecting...",self)
        self.exitButton = QPushButton("EXIT", self)
        self.button.setFont(QFont('Times', 45))
        self.button.clicked.connect(self.buttonCallback)
        self.exitButton.clicked.connect(self.exit)
        return

    def exit(self):
        sys.exit(0)
        return

    def setWinnerStyle(self):
        self.button.setText("Winner!")
        self.button.setStyleSheet("background-color: yellow")
        self.button.setEnabled(False)
        #self.button.repaint()
        return

    def enableButton(self):
        self.button.setEnabled(True)
        return

    def setButtonText(self, text):
        if text == "Game Over":
            self.button.setStyleSheet("background-color : red")
        else:
            self.button.setText(text)
            self.button.setStyleSheet("")
            #self.button.repaint()
        return

def buttonCallback():
    global currIdx
    global guiobj
    global nums
    global winNum
    global iWonFlag
    globalDataLock.acquire()

    if len(nums) > 0:
        # If we won
        if (currIdx != -1) & (nums[currIdx] == winNum):
            guiobj.setWinnerStyle()
            iWonFlag.lock()
            iWonFlag.set_int(1)
            iWonFlag.unlock()

        else:
            currIdx = currIdx + 1

            if currIdx >= len(nums):
                guiobj.setButttonText("Game Over")
            else:
                guiobj.setButtonText(str(nums[currIdx]))


    globalDataLock.release()
    return

def setupGUI():
    global App
    global guiobj
    App = QApplication(sys.argv)
    guiobj = GameWindow(buttonCallback)
    App.exec()

def main():
    global conn
    global restartFlag
    global guiobj
    
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

    # Setup the GUI object and return it
    guithread = Thread(target=setupGUI)
    guithread.start()

    print('GUI set up')

    # Now we loop waiting for a restart game signal
    while True:
        restartFlag.lock()
        if restartFlag.get_int() == 1:
            guiobj.setButtonText('RESTARTINGGGGG!')
            guiobj.enableButton()
            restartFlag.set_int(0)
        restartFlag.unlock()

    time.sleep(5)

    print('Worker done')
    return


main()
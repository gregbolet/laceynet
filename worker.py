from config import *
from threading import Lock, Thread
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

conn = None
nums = []
winNum = -1
currIdx = -1
restartFlag = AtomicInt(0)
iWonFlag = AtomicInt(0)
#isRegFlag = AtomicInt(0)
globalDataLock = Lock()
guiobj = None

class SenderThread:
    def __init__(self):
        print('Init a sender thread!')
        self.last_heartbeat = None

    def __register_worker(self):
        global conn

        reg_req = WorkerMsg(WorkerMsg.REGISTER)
        send_msg(conn, reg_req)
        print('Sent registration request!')

    def __send_heartbeat(self):
        global conn

        beat = WorkerMsg(WorkerMsg.HEARTBEAT)
        send_msg(conn, beat)
        self.last_heartbeat = get_cts()
        print('Sent heartbeat!')

    def __check_if_won(self):
        global iWonFlag
        global restartFlag
        
        iWonFlag.lock()
        restartFlag.lock()
        # winning condition: win flag true AND game started
        if iWonFlag.get_int() == 1 and restartFlag.get_int() == 1:
            restartFlag.unlock()
            iWonFlag.unlock()
            return True
        restartFlag.unlock()
        iWonFlag.unlock()
        return False

    def do_heartbeat(self):
        # Check if we need to send a heartbeat
        should_send_beat = (self.last_heartbeat == None) or (get_ts_diff(get_cts(), self.last_heartbeat) > HEARTBEAT_INTERVAL)

        if should_send_beat:
            self.__send_heartbeat()

    # This is what the threading.Thread.start will call 
    def __call__(self, *args, **kwargs):
        global conn
        print("Forked sender thread")

        # Get ourselves registered
        self.__register_worker()

        while True:
            self.do_heartbeat()

            if self.__check_if_won():
                winnermsg = WorkerMsg(WorkerMsg.IWON)
                send_msg(conn, winnermsg)
                iWonFlag.lock()
                iWonFlag.set_int(0) # set to not won
                iWonFlag.unlock()


class RecvThread:
    def __init__(self):
        print('Init receiving thread!')

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
        global guiobj
        print("Forked recv thread")

        # Handle restart/continue requests
        while True:
            # Expecting a confirmation back
            conf = conn.recv(MSG_BUFF_SIZE)
            print('Got a server response!')

            if not conf:
                print("[error] timeout")
                sys.exit(-1)
            else:
                # return a ControllerMsg object
                resp = pickle.loads(conf)
                print('Unpickled response object!')

                # if received a continue message from server
                if resp.response is ControllerMsg.CONTINUE:
                    print('Continuing game...')

                elif resp.response is ControllerMsg.GAME_START:
                    print('Restarting game...')

                    globalDataLock.acquire()
                    restartFlag.lock()
                    # iWonFlag.lock()
                    restartFlag.set_int(1)
                    # iWonFlag.set_int(0)

                    nums = resp.numbers_to_guess
                    winNum = resp.winning_num
                    # Start at one index behind
                    currIdx = -1
                    print('Got new restart data: numbers', nums)
                    print('Got new restart data: winNum ', winNum)

                    # restartFlag.lock()
                    if restartFlag.get_int() == 1:
                        guiobj.setButtonText('Starting')
                        guiobj.enableButton()
                        restartFlag.set_int(0)
                    # restartFlag.unlock()

                    # iWonFlag.unlock()
                    restartFlag.unlock()
                    globalDataLock.release()


class GameWindow(QMainWindow):
    def __init__(self, callback):
        super().__init__()
        self.button_callback = callback
        self.setWindowTitle("Blockchain")
        self.UIComponents()
        print('Setup UI components!')
        self.showFullScreen()
        print('made fullscreen!')
        self.setUIGeometries()
        print('set geometries!')

    def setUIGeometries(self):
        button_width = 1000
        button_height = 1000
        self.button.setGeometry(self.width()//2-button_width//2, self.height()//2-button_height//2, button_width, button_height)
        self.exitButton.setGeometry(100,100,250,250)

    def UIComponents(self):
        self.button = QPushButton("Waiting...",self)
        self.exitButton = QPushButton("EXIT", self)
        self.button.setFont(QFont('Times', 45))
        self.button.clicked.connect(self.button_callback)
        self.exitButton.clicked.connect(self.exit)

    def exit(self):
        sys.exit(0)

    def setWinnerStyle(self):
        self.button.setText("Winner!")
        self.button.setStyleSheet("background-color: yellow")
        self.button.setEnabled(False)
        #self.button.repaint()

    def enableButton(self):
        self.button.setEnabled(True)

    def setButtonText(self, text):
        if text == "Game Over":
            self.button.setStyleSheet("background-color : red")
            self.button.setText(text)
        else:
            self.button.setText(text)
            self.button.setStyleSheet("")
        #self.button.repaint()


def button_callback():
    global currIdx
    global guiobj
    global nums
    global winNum
    global iWonFlag

    globalDataLock.acquire()

    if len(nums) > 0:
        # If we won
        print("current index: {}".format(currIdx))
        if (currIdx != -1) and (nums[currIdx] == winNum):
            guiobj.setWinnerStyle()

            iWonFlag.lock()
            iWonFlag.set_int(1)
            iWonFlag.unlock()

        else:
            currIdx = currIdx + 1

            if currIdx >= len(nums):
                guiobj.setButtonText("Game Over")
            else:
                print("button callback! {}".format(nums))
                guiobj.setButtonText(str(nums[currIdx]))

    globalDataLock.release()

"""
def setup_gui():
    global App
    global guiobj

    App = QApplication(sys.argv)
    guiobj = GameWindow(button_callback)
    # App.exec()
    sys.exit(App.exec())
"""

def main():
    global conn
    global restartFlag
    global guiobj
    
    print('Starting worker!')
    print('Establishing Connection...')

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.settimeout(30)
    conn.connect((HOST, PORT))

    print('Connection READY!')

    recv_thread   = Thread(target = RecvThread())
    sender_thread = Thread(target = SenderThread())

    # Tell the threads to start running
    sender_thread.start()
    recv_thread.start()

    print('Sender + Receiver Threads Started')
    print('Now moving onto GUI...')

    # Setup the GUI object and return it
    # gui_thread = Thread(target=setup_gui)
    # gui_thread.start()

    app = QApplication(sys.argv)
    guiobj = GameWindow(button_callback)
    # app.exec()
    sys.exit(app.exec())

    print('GUI set up')

    # Now we loop waiting for a restart game signal
    # while True:
    #     restartFlag.lock()
    #     if restartFlag.get_int() == 1:
    #         guiobj.setButtonText('RESTARTINGGGGG!')
    #         guiobj.enableButton()
    #         restartFlag.set_int(0)
    #     restartFlag.unlock()

    time.sleep(5)

    print('Worker done')
    return


main()
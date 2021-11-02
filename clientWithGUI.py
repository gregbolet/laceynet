from lacey import *
from _thread import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys, random

class laceyPlayer:
    def __sendHeartbeat(self, s):
        beat = WorkerMsg(WorkerMsg.HEARTBEAT)
        sendMsg(s, beat)
        self.lastHeartbeat = getCTS()
        print('Sent heartbeat!')
        self.__waitForServerResponse(s)
        #print('Got heartbeat response')
        return

    def __registerWorker(self, s):
        regReq = WorkerMsg(WorkerMsg.REGISTER)
        sendMsg(s, regReq)
        print('Sent registration request!')
        self.__waitForServerResponse(s)
        print('Got registration response')

    # Update client state based on server responses
    def __waitForServerResponse(self,s):
        # Expecting a confirmation back
        conf = s.recv(MSG_BUFF_SIZE)

        # return a ControllerMsg object
        resp = pickle.loads(conf)

        if resp.response is ControllerMsg.CONTINUE:
            print('Continuing game...')

        elif resp.response is ControllerMsg.GAME_RESTART:
            print('Restarting game!')
            self.restartGame = True
            self.myNumbers = resp.numbersToGuess
            self.winningNum = resp.winningNum
            print(self.myNumbers)
            print(self.winningNum)

        else:
            self.iAmRegistered = False
            print('Stopping game...')

        return

    def doHeartbeat(self,s):
        # Check if we need to send a heartbeat
        shouldSendBeat = (self.lastHeartbeat == None) or (getTSDiff(getCTS(), self.lastHeartbeat) > HEARTBEAT_INTERVAL)

        if shouldSendBeat:
            self.__sendHeartbeat(s)

        return

    def connThread(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))

            # register ourselves with the server -- assume it completes
            self.__registerWorker(s)

            while True:
                #print('doing the heartbeat as i should')
                self.doHeartbeat(s)

        except Exception as e:
            print('Exception!!!', e)
        finally:
            print('Closing connection!')
            s.close()
            return

    # This updates the client's state based on
    def buttonClickCallback(self,button):
        # We will only change the button text if the game has started
        if len(self.myNumbers) > 0:
            if self.restartGame:
                print('Updating GUI for game RESTART!')
                self.restartGame = False     
                self.currGuessIndex = 0
                button.setEnabled(True)
                button.setText(str(self.myNumbers[self.currGuessIndex]))
                button.setStyleSheet("")
            else:
                self.currGuessIndex = self.currGuessIndex +1
                if self.currGuessIndex > len(self.myNumbers):
                    button.setText("Game Over")
                    button.setStyleSheet("background-color : red")
                    self.restartGame = True
                elif self.currGuessIndex -1 > -1 and self.myNumbers[self.currGuessIndex -1] == self.winningNum:
                    button.setText("Winner!")
                    button.setStyleSheet("background-color : yellow")
                    button.setEnabled(False)
                else:
                    if self.currGuessIndex >= len(self.myNumbers):
                        button.setStyleSheet("background-color : red")
                        button.setText("Game Over")
                        self.restartGame = True
                    else:   
                        button.setText(str(self.myNumbers[self.currGuessIndex]))
        return

    def __init__(self):
        self.lastHeartbeat = None
        self.iAmRegistered = False
        self.restartGame = False
        self.myNumbers = []
        self.winningNum = -1
        self.currGuessIndex = 0
        print("Starting Worker!")

        start_new_thread(self.connThread, ())

        # Do nothing for now
        # while True:
        #     continue

        return

class GameWindow(QMainWindow):
    def __init__(self,myplayer):
        super().__init__()
        self.player = myplayer
        self.setWindowTitle("Blockchain Guessing Game")
        self.UIComponents()
        self.showFullScreen()
        self.setUIGeometries()
        
        #print(self.width(),self.height())

    def setUIGeometries(self):
        buttonWidth = 1000
        buttonHeight = 1000
        self.button.setGeometry(self.width()//2-buttonWidth//2,self.height()//2-buttonHeight//2,buttonWidth,buttonHeight)
        self.exitButton.setGeometry(100,100, 250,250)

    def UIComponents(self):
        self.button = QPushButton("Connecting...", self)
        self.exitButton = QPushButton("EXIT",self)
        self.button.setFont(QFont('Times', 45))
        self.button.clicked.connect(lambda: self.player.buttonClickCallback(self.button))
        self.exitButton.clicked.connect(self.exit)
        #self.button.setText("Start")

    def exit(self):
        sys.exit(App.exec())


App = QApplication(sys.argv)
myplayer = laceyPlayer()
window = GameWindow(myplayer)
sys.exit(App.exec())

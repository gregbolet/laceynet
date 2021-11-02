from lacey import *
from _thread import *

class laceyPlayer:
    def doHeartbeat(self,s):
        # Check if we need to send a heartbeat
        shouldSendBeat = (self.lastHeartbeat == None) or (getTSDiff(getCTS(), self.lastHeartbeat) > HEARTBEAT_INTERVAL)

        if shouldSendBeat:
            self.__sendHeartbeat(s)

        return

    def __sendHeartbeat(self, s):
        beat = WorkerMsg(WorkerMsg.HEARTBEAT)
        sendMsg(s, beat)
        self.lastHeartbeat = getCTS()
        print('Sent heartbeat!')
        self.__waitForServerResponse(s)
        print('Got heartbeat response')
        return

    def __registerWorker(self, s):
        regReq = WorkerMsg(WorkerMsg.REGISTER)
        sendMsg(s, regReq)
        print('Sent registration request!')

        self.__waitForServerResponse(s)

    # Update client state based on server responses
    def __waitForServerResponse(self,s):
        # Expecting a confirmation back
        conf = s.recv(MSG_BUFF_SIZE)
        print('Got a server response!')

        # return a ControllerMsg object
        resp = pickle.loads(conf)
        print('Unpickled response object!')

        if resp.response is ControllerMsg.CONTINUE:
            print('Continuing game...')

        elif resp.response is ControllerMsg.GAME_RESTART:
            print('Restarting game!')
            self.restartGame = True
            self.myNumbers = resp.numbersToGuess
            self.winningNum = resp.winningNum

        else:
            self.iAmRegistered = False
            print('Stopping game...')

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
    def buttonClickCallback(self):
        # We will only change the button text if the game has started
        if self.iAmRegistered:
            if self.restartGame:
                print('Updating GUI for game RESTART!')
                self.restartGame = False
            


        return

    def __init__(self):
        self.lastHeartbeat = None
        self.iAmRegistered = False
        self.restartGame = False
        self.myNumbers = []
        self.winningNum = -1
        print("Starting Worker!")

        start_new_thread(self.connThread, ())

        # Do nothing for now
        while True:
            continue

        return


myplayer = laceyPlayer()
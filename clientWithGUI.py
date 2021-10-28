from lacey import *
from _thread import *

class laceyPlayer:
    def __sendHeartbeat(self, s):
        self.lastHeartbeat = getCTS()
        beat = WorkerMsg(WorkerMsg.HEARTBEAT)
        sendMsg(s, beat)
        print('Sent heartbeat!')
        return

    def __registerWorker(self, s):
        regReq = WorkerMsg(WorkerMsg.REGISTER)
        sendMsg(s, regReq)

        self.__waitForServerResponse(s)

    # Update client state based on server responses
    def __waitForServerResponse(self,s):
        # Expecting a confirmation back
        conf = s.recv(MSG_BUFF_SIZE)

        # return a ControllerMsg object
        resp = pickle.loads(conf)

        if resp.response is ControllerMsg.CONTINUE:
            print('Continuing game...')

        elif resp.response is ControllerMsg.REGIST_SUCC:
            print('Registered with server!')
            self.iAmRegistered = True
            self.myNumbers = resp.numbersToGuess
            self.winningNum = resp.winningNum

        elif resp.response is ControllerMsg.GAME_RESTART:
            print('Restarting game!')
            self.restartGame = True
            self.myNumbers = resp.numbersToGuess
            self.winningNum = resp.winningNum

        else:
            self.iAmRegistered = False
            print('Stopping game...')

        return

    def doHeartbeat(self,s):
        # Check if we need to send a heartbeat
        shouldSendBeat = (self.lastHeartbeat == None) or (getTSDiff(getCTS(), self.lastHeartbeat) > HEARTBEAT_INTERVAL)

        if shouldSendBeat:
            self.__sendHeartbeat(s)

        self.__waitForServerResponse(s)
        return

    def connThread(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))

            # register ourselves with the server -- assume it completes
            self.__registerWorker(s)

            while True:
                self.doHeartbeat(s)
        finally:
            s.close()
            return

    def __init__(self):
        self.lastHeartbeat = None
        self.haveNumbers = False
        self.iAmRegistered = False
        self.restartGame = False
        self.myNumbers = []
        self.winningNum = -1
        print("Starting Worker!")

        start_new_thread(self.connThread, ())

        return


myplayer = laceyPlayer()
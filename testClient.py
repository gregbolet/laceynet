#!/usr/bin/env -S PYTHONPATH=../common python3

from config import *

class LaceyPlayer:
    def __send_heartbeat(self, s):
        self.last_heartbeat = get_cts()
        beat = WorkerMsg(WorkerMsg.HEARTBEAT)
        send_msg(s, beat)
        print('Sent heartbeat!')


    def __register_worker(self, s):
        reg_req = WorkerMsg(WorkerMsg.REGISTER)
        send_msg(s, reg_req)

        # Expecting a confirmation back
        conf = s.recv(MSG_BUFF_SIZE)
        print('Im registered!')
        # return a ControllerMsg object
        return pickle.loads(conf)


    def __init__(self):
        self.last_heartbeat = None
        print("Starting Worker!")

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))

        # register ourselves with the server
        cntrl_msg = self.__register_worker(s)
        if cntrl_msg.response is not ControllerMsg.GAME_RESTART:
            print('Could not get registered to controller!')
            return
        else:
            print('Succesfully Registered!')


        while True:

            # Check if we need to send a heartbeat
            should_send_beat = (self.last_heartbeat == None) or (get_ts_diff(get_cts(), self.last_heartbeat) > HEARTBEAT_INTERVAL)

            if should_send_beat:
                self.__send_heartbeat(s)

        # Close the socket connection
        s.close()

def main():
    LaceyPlayer()

if __name__=="__main__":
    main()

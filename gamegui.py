from lacey import *
import button

 #!/bin/bash
#source https://github.com/clear-code-projects/elevatedButton/blob/main/button.py
import pygame
import sys
import time
import os
import numpy

from pygame.constants import NUMEVENTS


class GameGui:

    def __registerWorker(self, s):
        regReq = WorkerMsg(WorkerMsg.REGISTER)
        sendMsg(s, regReq)

        # Expecting a confirmation back
        conf = s.recv(MSG_BUFF_SIZE)

        # return a ControllerMsg object
        return pickle.loads(conf)

    def __sendHeartbeat(self, s):
        self.lastHeartbeat = getCTS()
        beat = WorkerMsg(WorkerMsg.HEARTBEAT)
        sendMsg(s, beat)
        print('Sent heartbeat!')
        return

    def startConnection(self):
        self.lastHeartbeat = None
        print("Starting Worker!")

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))

        # register ourselves with the server
        self.contrlMsg = self.__registerWorker(s)
        if self.contrlMsg.response is not ControllerMsg.REGIST_SUCC:
            print('Could not get registered to controller!')
            return None
        else:
            print('Succesfully Registered!')
            return s

    def setupBoard(self): 
        pygame.init()
        self.size = 700 #700
        self.screen = pygame.display.set_mode(
            (0,0), pygame.FULLSCREEN | pygame.RESIZABLE)
        self.width, self.height = self.screen.get_size()
        #print(self.width, self.height)
        #self.orientation = self.checkOrientation()
        pygame.display.set_caption('Guessing Game')
        self.clock = pygame.time.Clock()
        self.gui_font = pygame.font.Font(None, 250)
        self.font = pygame.font.SysFont(None, 65)
        self.currIndex = -1#-1
        self.currNum =  -1#-1 # current numbers
        self.guessedNum = -1 #-1 #previous number
        self.message = ""
    

        self.button1 = button.Button("Start", self.size, self.size, ((self.width // 2) - (
            self.size / 2), (self.height // 2)-(self.size / 2)), 15, False, self.screen, self.gui_font, self.clickEvent)
        self.exitButton = button.Button(
            "Exit", 150, 150, (10, 10), 5, True, self.screen, self.font,self.clickEvent)

    #Sets the list of numbers
    def getMyNums(self):
        self.myNums = self.contrlMsg.numbersToGuess
        self.winningNum = self.contrlMsg.winningNum
        print("winner")
        print(self.winningNum)

    #determines if we're in portrait or landscape mode
    def checkOrientation(self):
        if self.width > self.height:
            #landscape
            return 0
        else:
            #portrait
            return 1

    #gets the next number and updates the guessednumber
    def clickEvent(self):
        if self.currIndex == -1:
            self.currIndex = self.currIndex +1
            self.currNum = self.myNums[self.currIndex]
            self.button1.currNum = self.myNums[self.currIndex]
        elif self.currIndex + 1 < len(self.myNums): 
            self.guessedNum = self.currNum
            if self.guessedNum != self.winningNum:
                self.currIndex = self.currIndex+1
                self.currNum = self.myNums[self.currIndex]
                self.button1.currNum = self.myNums[self.currIndex]
            else:
                self.button1.currNum = "Congrats!"
                self.button1.game_over = True
        else: #essentially at the last number
            self.guessedNum = self.currNum
            if self.guessedNum == self.winningNum:
                self.guessedNum = self.currNum
                self.button1.currNum= "Congrats!"
                self.button1.game_over = True
            else:
                self.button1.currNum = "Game Over"
                self.currNum = "Game Over"
                self.button1.game_over = True

    #updates screen on click events
    def checkForClicks(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        #self clicking functonality
        #time = how long it waits until another click
        currTime = time.time()
        if currTime - self.button1.lastTimePressed > 30 and not(self.button1.game_over):
            pygame.mouse.set_pos(
                [(self.width/2) - (self.size/2), (self.height/2) - (self.size/2)])
            self.button1.pressed = True
            self.button1.check_click()

        self.screen.fill('#DCDDD8')
        self.button1.draw()
        self.exitButton.draw()
        self.message_to_screen(self.message) 
        pygame.display.update()          
        self.clock.tick(60)

    #Determines if we've won or lost the game
    def isWinner(self):
        if self.guessedNum == self.winningNum:
            self.message = "Congrats, you guessed the correct answer: " + str(self.guessedNum) + ". You win!"
        elif self.currNum == "Game Over":
            self.message = "Game over, better luck next time!"
        else:
            if self.guessedNum == -1:
                self.message = "Let's start guessing!"
            else:
                self.message = "You guessed " + str(self.guessedNum)+ ", keep trying!"

    #does heartbear
    def doHeartbeat(self, s):
        # Check if we need to send a heartbeat
        shouldSendBeat = (self.lastHeartbeat == None) or (
            getTSDiff(getCTS(), self.lastHeartbeat) > HEARTBEAT_INTERVAL)

        if shouldSendBeat:
            self.__sendHeartbeat(s)

    #Prints a given message to screen based on size 
    def message_to_screen(self, msg):
        orien = self.checkOrientation()
        if orien == 0: #landscape
                screen_text = self.font.render(msg, True, (255, 0,0))
                self.screen.blit(screen_text, (100, self.height - 100))
        else: #portrait
            if len(msg) >= 34: # if it doesnt fit the screen
                length = len(msg)
                screen_text = self.font.render(msg[0:33], True,(255,0,0))
                self.screen.blit(screen_text, (100, self.height - 200))
                screen_text2 = self.font.render(msg[34:length], True,(255,0,0))
                self.screen.blit(screen_text2, (100, self.height - 100))
            else:
                screen_text = self.font.render(msg, True, (255, 0,0))
                self.screen.blit(screen_text, (150, self.height - 100))

    def __init__(self):
        s = self.startConnection()
        self.setupBoard()
        self.getMyNums()

        while True:
            #self.isGameStarted()
            self.checkForClicks()
            self.doHeartbeat(s)
            self.isWinner()
                


game = GameGui()




                # elif event.type == pygame.VIDEORESIZE:
                #     #for flipping orientation ignore
                #     # print("currsize: " + (str(width)+ " "+str(height)))
                #     width, height =  event.size
                #     #print("newsize: " + (str(width)+ " "+str(height)))
                #     screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.RESIZABLE)
                #     self.button1.updateLoc(width,height, self.size)
                #     #print(button1.bottom_rect.width)
                #     #print(button1.bottom_rect.height)
                #     self.button1.draw()
                #     self.exitButton.draw()
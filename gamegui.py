from lacey import *

 #!/bin/bash
#source https://github.com/clear-code-projects/elevatedButton/blob/main/button.py
import pygame
import sys
import time
import os
import numpy

from pygame.constants import NUMEVENTS


class Button:
    def __init__(self, text, width, height, pos, elevation, exit, screen, myFont, onClickEvent):
        #Core attributes
        self.pressed = False
        self.elevation = elevation
        self.dynamic_elecation = elevation
        self.original_y_pos = pos[1]
        self.lastTimePressed = time.time()
        self.currNum = str(0)
        #true if exit button, false else
        self.exitButton = exit
        self.pos = pos
        self.screen = screen
        self.font = myFont
        self.currIndex = 0
        self.myNums = []
        self.game_over = False
        self.onClickEvent = onClickEvent
        # top rectangle
        self.top_rect = pygame.Rect(pos, (width, height))
        self.top_color = '#475F77'

        # bottom rectangle
        self.bottom_rect = pygame.Rect(pos, (width, height))
        self.bottom_color = '#354B5E'
        #text
        self.text_surf = self.font.render(text, True, '#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

    #updating button location
    def updateLoc(self, newW, newH, size):
        self.pos = ((newW // 2) - (size / 2), (newH//2)-(size / 2))
        self.original_y_pos = self.pos[1]

    def getMyNums(self, list):
        self.myNums = list

    #need to write errorr check for this
    def getNextNum(self):
        curr = self.currIndex
        if curr < len(self.myNums):
            return self.myNums[curr]

    def draw(self, numToWrite):
        # elevation logic
        #self.update_button()
        self.top_rect.y = self.original_y_pos - self.dynamic_elecation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elecation

        pygame.draw.rect(self.screen, self.bottom_color,
                         self.bottom_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.top_color,
                         self.top_rect, border_radius=12)
        self.screen.blit(self.text_surf, self.text_rect)
        if(self.exitButton):
            self.check_click_Exit()
        else:
            self.check_click(numToWrite)

    #function for exit button
    def check_click_Exit(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            self.top_color = '#D74B4B'
            if pygame.mouse.get_pressed()[0]:
                self.dynamic_elecation = 0
                self.pressed = True
            else:
                self.dynamic_elecation = self.elevation
                if self.pressed == True:
                    #numfile.close()
                    print('We are exiting the program, thanks for playing!')
                    self.pressed = False
                    pygame.quit()
                    sys.exit()

        else:
            self.dynamic_elecation = self.elevation
            self.top_color = '#475F77'

    #function for normal button
    def check_click(self, numToWrite):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            self.top_color = '#D74B4B'
            if pygame.mouse.get_pressed()[0]:
                self.dynamic_elecation = 0
                self.pressed = True
            else:
                self.dynamic_elecation = self.elevation
                if self.pressed == True:
                    self.lastTimePressed = time.time()

                    #self.currNum = numToWrite
                    self.onClickEvent()
                    self.text_surf = self.font.render(
                        str(self.currNum), True, '#FFFFFF')
                    self.text_rect = self.text_surf.get_rect(
                        center=self.top_rect.center)
                    self.screen.blit(self.text_surf, self.text_rect)
                    #print(printString)
                    self.pressed = False
        else:
            self.dynamic_elecation = self.elevation
            self.top_color = '#475F77'


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
        #move this
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

    def setupBoard(self):  # should this be init?
        pygame.init()
        self.size = 700
        #global screen
        self.screen = pygame.display.set_mode(
            (0, 0), pygame.FULLSCREEN | pygame.RESIZABLE)
        self.width, self.height = self.screen.get_size()
        print(self.width, self.height)
        pygame.display.set_caption('Guessing Game')
        self.clock = pygame.time.Clock()
        self.gui_font = pygame.font.Font(None, 250)
        self.font = pygame.font.SysFont(None, 65)
        self.currIndex = 0
        self.currNum = -1
        self.message = "winner"
        red = (255, 0, 0)
        currTime = time.time()

        name = "n1"  # name of node/machine for reading file

        #game_over = False
        message = ""
        self.button1 = Button("Start", self.size, self.size, ((self.width // 2) - (
            self.size / 2), (self.height // 2)-(self.size / 2)), 15, False, self.screen, self.gui_font, self.clickEvent)
        self.exitButton = Button(
            "Exit", 150, 150, (10, 10), 5, True, self.screen, self.font,self.clickEvent)

    def getMyNums(self):
        self.myNums = self.contrlMsg.numbersToGuess
        self.winningNum = self.contrlMsg.winningNum
        print("winner")
        print(self.winningNum)
        #self.button1.getMyNums(myNums)
        #winner = winning number

    def getNextNum(self):
        curr = self.currIndex
        if curr == 0:
            return -1
        if curr < len(self.myNums):
            return self.myNums[curr]
        else:
            return "Game Over"

    def clickEvent(self):
       
        if self.currIndex < len(self.myNums):
            self.currNum = self.myNums[self.currIndex]
            self.button1.currNum = self.myNums[self.currIndex]
            self.currIndex = self.currIndex+1
        else:
            self.button1.currNum = "Game Over"

    def checkForClicks(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #numfile.close()
                pygame.quit()
                sys.exit()

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

            #self clicking functonality
            #time = how long it waits until another click
        currTime = time.time()
        if currTime - self.button1.lastTimePressed > 30 and not(self.button1.game_over):
                #print("self click")
            pygame.mouse.set_pos(
                [(self.width/2) - (self.size/2), (self.height/2) - (self.size/2)])
            self.button1.pressed = True
            self.button1.check_click()

        self.screen.fill('#DCDDD8')
        self.currNum = self.getNextNum()
        #print(self.currNum)
        self.button1.draw(self.currNum)
        self.exitButton.draw(self.currNum)
        #message_to_screen(message)
        pygame.display.update()
        
        self.clock.tick(60)

    def isWinner(self):
        if self.currNum == self.winningNum:
            print("WINNER")
            self.message = "Congrats, you guessed the correct answer: " + str(self.currNum) + ". You win!"
            return True
        elif self.currNum == "Game Over":
            self.message = "Game over, sorry!"
            print("LOSER")
            return False
        else:
            print("still going")
            return False

    def doHeartbeat(self, s):
        # Check if we need to send a heartbeat
        shouldSendBeat = (self.lastHeartbeat == None) or (
            getTSDiff(getCTS(), self.lastHeartbeat) > HEARTBEAT_INTERVAL)

        if shouldSendBeat:
            self.__sendHeartbeat(s)

    def message_to_screen(self, msg):
        if len(msg) >= 34:
            #do something
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
            if self.isWinner():
                break
                self.message_to_screen(self.message)
            elif not(self.isWinner()) and len(self.message) > 0:
                self.message_to_screen(self.message)


game = GameGui()

#!/bin/bash
#source https://github.com/clear-code-projects/elevatedButton/blob/main/button.py
import pygame, sys, time, os

from pygame.constants import NUMEVENTS

class Button:
    def __init__(self,text,width,height,pos,elevation,exit):
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
        # top rectangle 
        self.top_rect = pygame.Rect(pos,(width,height))
        self.top_color = '#475F77'

        # bottom rectangle 
        self.bottom_rect = pygame.Rect(pos,(width,height))
        self.bottom_color = '#354B5E'
        #text
        if exit:
            global font
            self.text_surf = font.render(text, True, '#FFFFFF')
        else:
            self.text_surf = gui_font.render(text,True,'#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

    #updating button location
    def updateLoc(self, newW,newH, size):
        self.pos = ((newW // 2) - (size / 2),( newH//2)-(size /2))
        self.original_y_pos = self.pos[1]

    def draw(self):
        # elevation logic 
        #self.update_button()
        self.top_rect.y = self.original_y_pos - self.dynamic_elecation
        self.text_rect.center = self.top_rect.center 

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elecation

        pygame.draw.rect(screen,self.bottom_color, self.bottom_rect,border_radius = 12)
        pygame.draw.rect(screen,self.top_color, self.top_rect,border_radius = 12)
        screen.blit(self.text_surf, self.text_rect)
        if(self.exitButton):
            self.check_click_Exit()
        else:
            self.check_click()

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
                    numfile.close()                    
                    print('We are exiting the program, thanks for playing!')
                    self.pressed = False
                    pygame.quit()
                    sys.exit()
                    
        else:
            self.dynamic_elecation = self.elevation
            self.top_color = '#475F77'

    #function for normal button
    def check_click(self):
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
                    foundString = False
                    printString = ""
                    global game_over #signals if the game is over
                    global message #message to print to screen
                    while foundString == False and not(game_over):
                        currString = numfile.readline().strip().split(",") #list
                        if len(currString) <= 1:
                            #nothing in file, we reached the end
                            printString = "Game Over, thanks for playing!"
                            self.currNum = "Sorry!"
                            message = printString
                            foundString = True
                            game_over = True
                            
                        if currString[0] == name:
                            self.currNum = currString[1]
                            foundString = True
                            printString = "You guessed: " + self.currNum
                            if int(self.currNum) == int(winning):
                                printString = "Congrats, you guessed the correct answer: " + self.currNum + ". You win!"
                                message = printString 
                                game_over = True                  
                    
                    self.text_surf = gui_font.render(self.currNum,True,'#FFFFFF')
                    self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)
                    screen.blit(self.text_surf, self.text_rect)
                    print(printString)
                    self.pressed = False
        else:
            self.dynamic_elecation = self.elevation
            self.top_color = '#475F77'

os.environ['SDL_VIDEO_CENTERED'] = '1' #idk if this is needed
pygame.init()
size = 700
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN | pygame.RESIZABLE)
width, height = screen.get_size()
print(width,height)
pygame.display.set_caption('Guessing Game')
clock = pygame.time.Clock()
gui_font = pygame.font.Font(None,250)
font = pygame.font.SysFont(None, 65)

red = (255,0,0)
currTime = time.time()

name = "n1" #name of node/machine for reading file

game_over = False
message = ""

button1 = Button("Start",size,size,((width // 2) - (size / 2),(height //2)-(size /2)),15, False)
exitButton = Button("Exit", 150,150,(10, 10),5, True)

numfile = open("testfile.txt","r+")

#winning number is going to be the first line of the file
firstline = numfile.readline().split(",")
winning = firstline[1] #winning value 


#create start button to create window/buttons




#function to print message to screen
def message_to_screen(msg):
    if len(msg) >= 34:
        #do something
        length = len(msg)
        screen_text = font.render(msg[0:33],True,red)
        screen.blit(screen_text, (100, height - 200))
        screen_text2 = font.render(msg[34:length],True,red)
        screen.blit(screen_text2,(100, height - 100))
    else:
        screen_text = font.render(msg, True, red)
        screen.blit(screen_text,(150, height - 100))
   

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            numfile.close()
            pygame.quit()
            sys.exit()

        elif event.type == pygame.VIDEORESIZE:
            #for flipping orientation ignore
            # print("currsize: " + (str(width)+ " "+str(height)))
            width, height =  event.size
            #print("newsize: " + (str(width)+ " "+str(height)))
            screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.RESIZABLE)
            button1.updateLoc(width,height, size)
            #print(button1.bottom_rect.width)
            #print(button1.bottom_rect.height)
            button1.draw()
            exitButton.draw()
    
    #self clicking functonality
    #time = how long it waits until another click
    currTime = time.time()
    if currTime - button1.lastTimePressed > 30 and not(game_over):
        #print("self click")
        pygame.mouse.set_pos([(width/2) - (size/2),(height/2) - (size/2)])
        button1.pressed = True            
        button1.check_click() 
        
        
    screen.fill('#DCDDD8')
    button1.draw()
    exitButton.draw()
    message_to_screen(message)
    pygame.display.update()
    clock.tick(60)

    from lacey import * 

    class GameGui:
        

        def startConnection(self):
            def __init__(self): #move this
                self.lastHeartbeat = None
                print("Starting Worker!")

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((HOST, PORT))

                # register ourselves with the server
                cntrlMsg = self.__registerWorker(s)
                if cntrlMsg.response is not ControllerMsg.REGIST_SUCC:
                    print('Could not get registered to controller!')
                    return
                else:
                    print('Succesfully Registered!')


        def setupBoard(): #should this be init?
            pygame.init()
            size = 700
            global screen
            screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN | pygame.RESIZABLE)
            width, height = screen.get_size()
            print(width,height)
            pygame.display.set_caption('Guessing Game')
            clock = pygame.time.Clock()
            gui_font = pygame.font.Font(None,250)
            font = pygame.font.SysFont(None, 65)
            red = (255,0,0)
            currTime = time.time()

            name = "n1" #name of node/machine for reading file

            game_over = False
            message = ""
            global button1
            global exitButton
            button1 = Button("Start",size,size,((width // 2) - (size / 2),(height //2)-(size /2)),15, False)
            exitButton = Button("Exit", 150,150,(10, 10),5, True)

        def getMyNums():
            #response code??
            contrl = ControllerMsg(4)
            global myNums 
            myNums = contrl.numbersToGuess
            global winner 
             #winner = winning number

        def isGameStarted():

        def checkForClicks():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    numfile.close()
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE:
                    #for flipping orientation ignore
                    # print("currsize: " + (str(width)+ " "+str(height)))
                    width, height =  event.size
                    #print("newsize: " + (str(width)+ " "+str(height)))
                    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.RESIZABLE)
                    button1.updateLoc(width,height, size)
                    #print(button1.bottom_rect.width)
                    #print(button1.bottom_rect.height)
                    button1.draw()
                    exitButton.draw()
            
            #self clicking functonality
            #time = how long it waits until another click
            currTime = time.time()
            if currTime - button1.lastTimePressed > 30 and not(game_over):
                #print("self click")
                pygame.mouse.set_pos([(width/2) - (size/2),(height/2) - (size/2)])
                button1.pressed = True            
                button1.check_click() 
                
                
            screen.fill('#DCDDD8')
            button1.draw()
            exitButton.draw()
            message_to_screen(message)
            pygame.display.update()
            clock.tick(60)

        def isWinner(self, value):
            if value == winning:
                return True
            else:
                return False


        startConnection()
        setupBoard()
        getMyNums()

        while True:
            isGameStarted()
            checkForClicks()
            heartbeat()
            isWinner()


        
    


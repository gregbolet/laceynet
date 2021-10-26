  #!/bin/bash
#source https://github.com/clear-code-projects/elevatedButton/blob/main/button.py
import pygame, sys, time, os

from pygame.constants import NUMEVENTS

class Button:
    def __init__(self,text,width,height,pos,elevation,exit, screen, myFont):
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
        # top rectangle 
        self.top_rect = pygame.Rect(pos,(width,height))
        self.top_color = '#475F77'

        # bottom rectangle 
        self.bottom_rect = pygame.Rect(pos,(width,height))
        self.bottom_color = '#354B5E'
        #text        
        self.text_surf = self.font.render(text,True,'#FFFFFF')
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

        pygame.draw.rect(self.screen,self.bottom_color, self.bottom_rect,border_radius = 12)
        pygame.draw.rect(self.screen,self.top_color, self.top_rect,border_radius = 12)
        self.screen.blit(self.text_surf, self.text_rect)
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
                    #numfile.close()                    
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
                    
                    self.text_surf = self.font.render(self.currNum,True,'#FFFFFF')
                    self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)
                    self.screen.blit(self.text_surf, self.text_rect)
                    print(printString)
                    self.pressed = False
        else:
            self.dynamic_elecation = self.elevation
            self.top_color = '#475F77'
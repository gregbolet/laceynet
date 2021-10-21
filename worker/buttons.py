#source https://github.com/clear-code-projects/elevatedButton/blob/main/button.py
import pygame, sys, random, time, mouse

from pygame.constants import NUMEVENTS

class Button:
    def __init__(self,text,width,height,pos,elevation):
        #Core attributes 
        self.pressed = False
        self.elevation = elevation
        self.dynamic_elecation = elevation
        self.original_y_pos = pos[1]
        self.lastTimePressed = time.time()
        self.currNum = str(0)
        # top rectangle 
        self.top_rect = pygame.Rect(pos,(width,height))
        self.top_color = '#475F77'

        # bottom rectangle 
        self.bottom_rect = pygame.Rect(pos,(width,height))
        self.bottom_color = '#354B5E'
        #text
        self.text_surf = gui_font.render(text,True,'#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

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
        self.check_click()
        

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
                    while foundString == False:
                        currString = numfile.readline().strip().split(",") #list
                        if len(currString) <= 1:
                            #nothing in file, we reached the end
                            self.currNum = "Game Over"
                            foundString = True
                            
                        if currString[0] == name:
                            self.currNum = currString[1]
                            foundString = True
                            if int(self.currNum) == int(winning):
                                print("You won!")
                                #figure out what to do at end of game
                            game_over = True
                    
                    
                    self.text_surf = gui_font.render(self.currNum,True,'#FFFFFF')
                    self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)
                    screen.blit(self.text_surf, self.text_rect)
                    print('The number pressed was '+ self.currNum)
                    self.pressed = False
        else:
            self.dynamic_elecation = self.elevation
            self.top_color = '#475F77'
   
    
pygame.init()
width = 1000
height = 1000
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption('Gui Menu')
clock = pygame.time.Clock()
timer_sec = 10
gui_font = pygame.font.Font(None,100)

currTime = time.time()

name = "n1"
game_over = False

button1 = Button("Start",500,500,(((width/2) - 250),((height/2))-250),5)

numfile = open("testfile.txt","r+")

#winnginf number is going to be the first line of the file
firstline = numfile.readline().split(",")
winning = firstline[1]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            numfile.close()
            pygame.quit()
            sys.exit()
        
       
        
    #mouse has to be on the window
    currTime = time.time()
    if currTime - button1.lastTimePressed > 3 and not(game_over):
        print("self click")
        pygame.mouse.set_pos([(width/2) - 250,(height/2)-250])
        button1.pressed = True            
        button1.check_click() 
        
        
    screen.fill('#DCDDD8')
    button1.draw()
    pygame.display.update()
    clock.tick(60)
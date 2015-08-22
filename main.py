import pygame
import fivenights
import webbrowser
from pygame.locals import *

def main():
    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Five Nights With Us')
    
    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    
    #BGM
    pygame.mixer.music.load('assets/sounds/Buzz_Fan_Florescent2.wav')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.4)
    buttonSound = pygame.mixer.Sound('assets/sounds/blip3.wav')
    victorySound = pygame.mixer.Sound('assets/sounds/music box.wav')
    loseSound = pygame.mixer.Sound('assets/sounds/chimes 2.wav')
    
    #BG animation
    menuBG = MenuBG()
    
    #Menu Buttons
    playGame = MenuButton([40,280], "Play Game")
    creditsButton = MenuButton([40,330], "Credits")
    quitGame = MenuButton([40,380], "Exit Game")
    versionText = MenuText([580,440], "V.0.6", 15)
    
    #Start Text
    guard1Text = MenuText([320,280], "Guard 1")
    guard1Text.center(0, -25)
    timeText = MenuText([320,330], "12:00 AM")
    timeText.center(0,25)
    
    #Credits Text
    credits1 = MenuText([40,40],  "Based on Five Nights at Freddy's by Scott Cawthon", 15)
    credits2 = MenuText([40,90],  "Sounds, animations, sprites, and scenario by Scott Cawthon", 15)
    credits3 = MenuText([40,140], "This is a non-profit fan game, no infringement is intended.", 15)
    credits4 = MenuText([40,190], "8-bit FNAF icons by R35TART on DeviantArt", 15)
    credits5 = MenuText([40,240], "http://r35tart.deviantart.com/", 15, True)
    credits6 = MenuText([40,340], "Programming by digiholic using Pygame", 15)
    backButton = MenuButton([40,390], "Back")
    urlOpen = False
    
    #Victory Screen
    victoryBG = VictoryBG()
    victoryText = MenuText([240,180], "You Win")
    
    #Loss Screen
    lossText = MenuText([320,240], "6 AM")
    timeText.center(0,0)
    
    menuObjects = []
    menuObjects.append(menuBG)
    menuObjects.append(playGame)
    menuObjects.append(creditsButton)
    menuObjects.append(quitGame)
    menuObjects.append(versionText)
    
    timeObjects = []
    timeObjects.append(guard1Text)
    timeObjects.append(timeText)
    
    creditsObjects = []
    creditsObjects.append(credits1)
    creditsObjects.append(credits2)
    creditsObjects.append(credits3)
    creditsObjects.append(credits4)
    creditsObjects.append(credits5)
    creditsObjects.append(credits6)
    creditsObjects.append(backButton)
    
    victoryObjects = []
    victoryObjects.append(victoryBG)
    victoryObjects.append(victoryText)
    victoryObjects.append(backButton)
    
    lossObjects = []
    lossObjects.append(lossText)
    lossObjects.append(backButton)
    
    objects = menuObjects[:]
    hoveredObjects = []
    
    clockStart = False
    clockTicks = 0
    time = pygame.time.get_ticks()
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return -1
            elif event.type == MOUSEBUTTONUP:
                mousepos = pygame.mouse.get_pos()
                clicked_sprites = [s for s in objects if s.rect.collidepoint(mousepos)]
                for obj in clicked_sprites:
                    if (obj == playGame):
                        buttonSound.play()
                        pygame.mixer.music.stop()
                        clockStart = True
                        objects = timeObjects[:]
                    elif (obj == quitGame):
                        return -1
                    elif (obj == creditsButton):
                        buttonSound.play()
                        objects = creditsObjects[:]
                    elif (obj == backButton):
                        victorySound.stop()
                        loseSound.stop()
                        buttonSound.play()
                        objects = menuObjects[:]
                    elif (obj == credits5):
                        if not urlOpen: webbrowser.open("http://r35tart.deviantart.com")
                        urlOpen = True
            elif event.type == MOUSEMOTION:
                mousepos = pygame.mouse.get_pos()
                hovered_sprites = [s for s in objects if s.rect.collidepoint(mousepos)]
                for obj in hovered_sprites:
                    obj.hovered = True
                    if hoveredObjects.count(obj) == 0: hoveredObjects.append(obj)
                for obj in hoveredObjects:
                    if hovered_sprites.count(obj) == 0:
                        obj.hovered = False
                        hoveredObjects.remove(obj)
            
            elif event.type == KEYUP:
                if event.key == pygame.K_ESCAPE:
                    if (clockStart):
                        clockStart = False
                        clockTicks = 0
                        objects = menuObjects[:]
                    else:
                        return -1
        if ((pygame.time.get_ticks() - time) >= 1000):
            if clockStart:
                time = pygame.time.get_ticks()
                clockTicks += 1
                if (clockTicks == 4):
                    buttonSound.play()
                    status = fivenights.game(screen,1,False)
                    if (status == -1): return -1
                    elif (status != 0):
                        #Put in different ending screens here.
                        #0 means loss, 1 means freddy win, 2 means bonnie win,
                        #3 means chica win, 4 means foxy win, 5 means quit
                        pygame.mixer.stop()
                        victorySound.play()
                        clockTicks = 0
                        clockStart = False
                        objects = victoryObjects[:]
                    elif (status == 0):
                        pygame.mixer.stop()
                        loseSound.play()
                        clockTicks = 0
                        clockStart = False
                        objects = lossObjects[:]
            
        screen.fill([0, 0, 0])
        for obj in objects:
            obj.update()
            screen.blit(obj.image,obj.rect)        
            
        pygame.display.update()
            
class MenuButton(pygame.sprite.Sprite):
    
    def __init__(self, topleft, text):
        pygame.sprite.Sprite.__init__(self)
        self.topleft = topleft
        self.text = text
        self.hovered = False
        
        self.font = pygame.font.Font("assets/Courier_New.ttf", 30)
        self.image = self.font.render("",1,[255,255,255])
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.topleft
        self.update()
    
    def update(self):
        self.image = pygame.Surface([20 + (18 * len(self.text)),45])
        #self.image = pygame.Surface([200,100])
        
        if (self.hovered): self.image.fill([128,128,128])
        else: self.image.fill([0,0,0])
        
        self.image.blit(self.font.render(self.text, 1,[255,255,255]), [10,5])
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.topleft
        
class MenuText(pygame.sprite.Sprite):    
    def __init__(self, topleft, text, size=30, underlined = False):
        pygame.sprite.Sprite.__init__(self)
        self.topleft = topleft
        self.text = text
        
        self.font = pygame.font.Font("assets/Courier_New.ttf", size)
        self.font.set_underline(underlined)
        self.image = pygame.Surface([20 + (18 * len(self.text)),45])
        
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.topleft
        
    def update(self):
        #self.image.fill([255,255,255])
        self.image = pygame.Surface([20 + (18 * len(self.text)),45])
        self.image.blit(self.font.render(self.text,1,[255,255,255]),[0,0])
        self.rect = self.image.get_rect()
        self.rect.topleft = self.topleft
    
    def center(self,xOff,yOff):
        x = round(self.image.get_size()[0]/2)
        y = round(self.image.get_size()[1]/2)
        self.topleft = [(320 - x + xOff),(240 - y + yOff)]
        
class MenuBG(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/menu0.png')
        self.delay = 5
        self.frame = 0
        
        self.rect = self.image.get_rect()
        self.rect.topleft = [-210,0]
        
    def update(self):
        if (self.delay == 0):
            if self.frame == 2: self.frame = 0
            else: self.frame += 1
            self.delay = 5
            self.image = pygame.image.load('assets/sprites/menu' + str(self.frame) + '.png')
        else:
            self.delay -= 1

class VictoryBG(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/victory.png')
        
        self.rect = self.image.get_rect()
        self.rect.topleft = [0,0]
        
            
if __name__  == '__main__': main()

import pygame, datetime, random
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_RETURN,
    KEYDOWN,
    QUIT,
)

#creates a dog object based on dog number
class Dog:
    def __init__(self, number):
        if number == 1:
            self.image = pygame.image.load("dog1.png").convert()
            self.image = pygame.transform.scale(self.image, [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2])
        self.surf = self.image
        self.rect = self.surf.get_rect()
        self.height = self.image.get_height()
        self.width = self.image.get_width()
    
#superclass for all loaded scenes
class Scene:
    def __init__(self, running):
        self.running = running
    def key_handler(keys):
        pass

    def loop(self):
         #log currently pressed keys
         keys_pressed = pygame.key.get_pressed()
         #pass currently pressed keys to keyhandler
         self.key_handler(keys_pressed)

#home class handles rendering and input for main game screen
class Home(Scene):
    menu = False

    def __init__(self, running):
        super(Home, self).__init__(running)
        self.current_dog = Dog(1)

    def key_handler(self, keys):
        #check for new events
         for key in keys:
             if key == K_ESCAPE:
                 self.running = False

    def loop(self):
        while self.running:
            #send keypresses to keyhandler
            super(Home, self).loop()
            #check for exit events
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                elif event.type == QUIT:
                    self.running = False
            #draw current dog on screen
            self.current_dog.rect = [SCREEN_WIDTH / 20, SCREEN_HEIGHT / 2 - self.current_dog.height / 2]
            screen.blit(self.current_dog.surf, self.current_dog.rect)
            #call new frame to render
            pygame.display.flip()


#initialize pygame module
pygame.init()
#define screen size
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
#load home scene and call its main render loop
current_scene = Home(True)
current_scene.loop()


#once main loop exits, close game
pygame.quit()

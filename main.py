import pygame, time, random, json, os.path
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

#defines dog stats per dog
class Stats:
    def __init__(self):
        #stats for dog gameplay
        self.data = {
            "health": 100,
            "love": 100,
            "happy": 100,
            "current": int(time.time()),
            "last": int(time.time()),
            "idle": 0
        }
        #if game has been played before, load stats from save file
        if os.path.exists("data.json"):
            with open("data.json") as read_file:
                data_json = json.load(read_file)
                self.data = data_json
                self.data['current'] = int(time.time())
                self.data['idle'] = self.data['current'] - self.data['last']
        #save new data or if first time playing, create save file with init data
        with open("data.json", "w+") as write_file:
            json.dump(self.data, write_file)
        
    #store current login time
    def exit_update(self):
        self.data['last'] = self.data['current']
        with open("data.json", "w+") as write_file:
            json.dump(self.data, write_file)

        
#defines menu surfaces based on input text/color
class Menu:
    def __init__(self, font_size, color, background, item_text):
        self.item_text = item_text
        self.font = pygame.font.Font('press_start.ttf', font_size)
        self.items = []
        for text in item_text:
            self.items.append(self.font.render(text, False, color, background))

#defines hud surfaces
class HUD:
    def __init__(self, dog):
        self.font_size = 28
        self.item_text = ["➕", "❤", "☺"]
        self.font = pygame.font.Font('press_start.ttf', self.font_size)
        self.items = [
            ["➕", dog.stats.data["health"], (255,255,255)],
            ["❤", dog.stats.data["love"], (255,0,0)],
            ["☺", dog.stats.data["happy"], (255,255,255)]
        ]
        self.surfaces = []
        for item in self.items:
            self.surfaces.append([self.font.render(item[0], False, item[2], None), 
            self.font.render(item[0], False, item[2], None)])

#creates a dog object based on dog number
class Dog:
    def __init__(self, number):
        if number == 1:
            self.image = pygame.image.load("dog1.png").convert()
            self.image = pygame.transform.scale(self.image, [RESOLUTION[0] / 2, RESOLUTION[1] / 2])
        self.surf = self.image
        self.rect = self.surf.get_rect()
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        self.stats = Stats()
    
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

    def __init__(self, running):
        super(Home, self).__init__(running)
        self.current_dog = Dog(1)
        self.menu = Menu(16, WHITE, None, ["Feed (F)", "Play (P)", "Love (L)"])
        self.hud = HUD(self.current_dog)
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
                        self.current_dog.stats.exit_update()
                elif event.type == QUIT:
                    self.running = False
                    self.current_dog.stats.exit_update()
            #draw current dog on screen
            self.current_dog.rect = [PIXEL * 5, screen.get_rect().center[1] / 2]
            screen.blit(self.current_dog.surf, self.current_dog.rect)
            #draw menu on screen
            for i in range(len(self.menu.items)):
                screen.blit(
                    self.menu.items[i],
                    [ PIXEL * 50,
                    ( (RESOLUTION[1] / 2) + self.menu.items[i].get_height() * (i) ) 
                    ])
            #call new frame to render
            pygame.display.flip()


#initialize pygame module
pygame.init()
#define screen size
RESOLUTION = (500,500)
#define pixel size aka grid size for object placement on screen
PIXEL = RESOLUTION[0] / 100
screen = pygame.display.set_mode(RESOLUTION)
#define colors
WHITE = (255,255,255)
#load home scene and call its main render loop
current_scene = Home(True)
current_scene.loop()


#once main loop exits, close game
pygame.quit()

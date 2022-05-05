import pygame, time, random, json, os.path
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_f,
    K_p,
    K_l,
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
    def get_health(self):
        return self.data['health']
    def get_love(self):
        return self.data['love']
    def get_happy(self):
        return self.data['happy']
    #store current login time
    def exit_update(self):
        self.data['last'] = self.data['current']
        with open("data.json", "w+") as write_file:
            json.dump(self.data, write_file)

        
#defines main_menu surfaces based on input text/color
class Menu:
    def __init__(self, font_size, color, background, item_text):
        self.font_size = font_size
        self.color = color
        self.background = background
        self.item_text = item_text
        self.font = pygame.font.Font('press_start.ttf', font_size)
        self.items = []
        self.draw()
    #draw items with no style applied
    def draw(self):
        self.items = []
        self.font.set_bold(False)
        self.font.set_underline(False)
        for text in self.item_text:
            self.items.append(self.font.render(text, False, self.color, self.background))

#defines hud surfaces
class HUD:
    def __init__(self, dog):
        self.dog = dog
        self.font_size = 24
        self.font = pygame.font.Font('press_start.ttf', self.font_size)
        self.cross_icon = pygame.image.load("cross_icon.png").convert()
        self.heart_icon = pygame.image.load("heart_icon.png").convert()
        self.happy_icon = pygame.image.load("happy_icon.png").convert()
        self.update(self.dog)
    def update(self, dog):
        self.dog = dog
        self.items = [
            [self.cross_icon, str(self.dog.stats.get_health()), (0,255,0)],
            [self.heart_icon, str(self.dog.stats.get_love()), (255,0,0)],
            [self.happy_icon, str(self.dog.stats.get_happy()), (255,255,0)]
        ]
        self.surfaces = []
        for item in self.items:
            self.surfaces.append([item[0], 
            self.font.render(item[1], False, item[2], None)])

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
    def feed(self):
        self.stats.data['health'] += 1
    def play(self):
        self.stats.data['happy'] += 1
    def love(self):
        self.stats.data['love'] += 1
    
#superclass for all loaded scenes
class Scene:
    def __init__(self, running):
        self.running = running

    def key_handler(keys):
        pass

    def loop(self):
        pass
         

#home class handles rendering and input for main game screen
class Home(Scene):
    def __init__(self, running):
        super(Home, self).__init__(running)
        self.current_dog = Dog(1)
        self.main_menu = Menu(20, WHITE, None, ["Feed (F)", "Play (P)", "Love (L)"])
        self.sub_menu = None
        self.hud = HUD(self.current_dog)
        self.flags = {
            "main_menu": True,
            "sub_menu": False,
            "feed": False,
            "play": False,
            "love": False
        }
        self.selected_item = 0
    def key_handler(self, key):
        #exit upon escape keypress, save dog stats first
        if key == K_ESCAPE:
            self.running = False
            self.current_dog.stats.exit_update()
        #if in main menu, display sub-menus on keypress
        if self.flags['main_menu']:
            if key == K_f:
                self.flags['sub_menu'] = True
                self.flags['feed'] = True
                self.sub_menu = Menu(20, BLACK, WHITE, ["Steak", "Veggies", "Snack", "Treat"])
            elif key == K_p:
                self.flags['sub_menu'] = True
                self.flags['play'] = True
                self.sub_menu = Menu(20, BLACK, WHITE, ["Ball", "Frisbee", "Tag", "Tricks"])
            elif key == K_l:
                self.flags['sub_menu'] = True
                self.flags['love'] = True
                self.sub_menu = Menu(20, BLACK, WHITE, ["Pet", "Snuggle", "Pat", "Praise"])
        #if in sub-menu, display highlighted items on keypress
        if self.flags['sub_menu']:
            if key == K_UP:
                self.selected_item -= 0 if self.selected_item < 2 else 2
            elif key == K_DOWN:
                self.selected_item += 2 if self.selected_item < 2 else 0
            elif key == K_LEFT:
                self.selected_item -= 1 if self.selected_item > 0 else 0
            elif key == K_RIGHT:
                self.selected_item += 1 if self.selected_item < 3 else 0
            #bold and underline selected item
            self.sub_menu.draw()
            self.sub_menu.font.set_underline(True)
            self.sub_menu.font.set_bold(True)
            self.sub_menu.items[self.selected_item] = self.sub_menu.font.render(
                self.sub_menu.item_text[self.selected_item], 
                False, BLACK, WHITE)
            #once sub-menu item is selected, update stats and hud accordingly and clear menu
            if key == K_RETURN:
                if self.flags['feed']:
                    self.current_dog.feed()
                elif self.flags['play']:
                    self.current_dog.play()
                elif self.flags['love']:
                    self.current_dog.love()
                self.hud.update(self.current_dog)
                self.clear_flags()
    #clear every flag except main menu
    def clear_flags(self):
        for flag in self.flags:
            if flag != "main_menu":
                self.flags[flag] = False

    def loop(self):
        while self.running:
            #inherit basic loop functionality from Scene super
            super(Home, self).loop()
            #check for events
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    self.key_handler(event.key)
                elif event.type == QUIT:
                    self.running = False
                    self.current_dog.stats.exit_update()
            #draw background
            screen.fill(BLACK)
            #draw current dog on screen
            self.current_dog.rect = [PIXEL * 5, screen.get_rect().center[1] / 2]
            screen.blit(self.current_dog.surf, self.current_dog.rect)
            #draw main_menu on screen
            for i in range(len(self.main_menu.items)):
                screen.blit(
                    self.main_menu.items[i],
                    [ PIXEL * 50,
                    ( (RESOLUTION[1] / 2) + self.main_menu.items[i].get_height() * (i * 1.5) ) 
                    ])
            #draw HUD on screen
            for i in range(len(self.hud.surfaces)):
                screen.blit(
                    self.hud.surfaces[i][0],
                    [ self.hud.surfaces[i][1].get_width() * (i * 2) + PIXEL * 10,
                    ( PIXEL * 10) 
                    ])
                screen.blit(
                    self.hud.surfaces[i][1],
                    [ self.hud.surfaces[i][1].get_width() * (i * 2) + PIXEL * 15,
                    ( PIXEL * 10) 
                    ])
            #draw sub-menu if opened
            if self.flags['sub_menu']:
                pygame.draw.rect(screen, WHITE, 
                    (0, #x
                    RESOLUTION[0] - PIXEL * 25, #y
                    RESOLUTION[0], #width
                    int(PIXEL * 25 ) #height
                    ) 
                )
                for i in range(len(self.sub_menu.items)):
                    screen.blit(
                        self.sub_menu.items[i],
                        [ PIXEL * 20 * (i * 1.5 if i < 2 else (i-2) * 1.5) + PIXEL * 20, #skip line after two items
                        ( RESOLUTION[0] - PIXEL * (20 if i < 2 else 10 )) #skip line after two items
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
BLACK = (0,0,0)
WHITE = (255,255,255)
#load home scene and call its main render loop
current_scene = Home(True)
current_scene.loop()


#once main loop exits, close game
pygame.quit()

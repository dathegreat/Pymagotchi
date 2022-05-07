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
 

class Overlay_Item:
    #create a new item with random x and y jitter
    def __init__(self, overlay):
        self.overlay = overlay
        self.x = PIXEL * 25 + (random.randint(1,5) * PIXEL)
        self.y = PIXEL * 40 + (random.randint(1,5) * PIXEL)
        self.frame_count = 0
    #float item upward and jitter x axis left or right based on frame count
    def jitter(self):
        self.frame_count += 1
        if self.frame_count == 4:
            if random.random() > 0.5:
                self.x -= PIXEL * 1
            else:
                self.x += PIXEL * 1
            self.y -= PIXEL * 1
            self.frame_count = 0

class Overlay:
    def __init__(self, overlay):
        self.current_overlay = overlay or None
        self.sad_icon = pygame.image.load("sad_icon.png").convert_alpha()
        self.poop_icon = pygame.image.load("poop_icon.png").convert_alpha()
        self.items = []
    #draw a new overlay item roughly once every other tick, and clear old items
    def draw(self, screen):
        if random.random() < 0.1:
            self.items.append(Overlay_Item(self.current_overlay))
        #clear old items
        if len(self.items) > 50:
            del(self.items[0])
        #draw and animate new items
        for item in self.items:
            screen.blit(item.overlay, (item.x, item.y))
            item.jitter()
    def stinky(self):
        self.current_overlay = self.poop_icon
    def sadness(self):
        self.current_overlay = self.sad_icon
    def get_overlay(self):
        return self.current_overlay

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
    def get_idle(self):
        return self.data['idle']

    def set_health(self, health):
        if self.get_health() < 100:
            self.data['health'] = health
    def set_love(self, love):
        if self.get_love() < 100:
            self.data['love'] = love
    def set_happy(self, happy):
        if self.get_happy() < 100:
            self.data['happy'] = happy
    #update stats based on idle time
    def instance_update(self):
        #subtract roughly ten points from each stat per idle day
        stats_decrement = int(self.get_idle() * (10/86400))
        self.set_health( self.get_health() - (stats_decrement) )
        self.set_love( self.get_love() - (stats_decrement) )
        self.set_happy( self.get_happy() - (stats_decrement) )
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
        self.cross_icon = pygame.image.load("cross_icon.png").convert_alpha()
        self.heart_icon = pygame.image.load("heart_icon.png").convert_alpha()
        self.happy_icon = pygame.image.load("happy_icon.png").convert_alpha()
        self.update(self.dog)
        self.ideal_stat_size = self.font.render("100", False, (0,0,0), None)

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
            self.image = pygame.image.load("dog1.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, [RESOLUTION[0] / 2, RESOLUTION[1] / 2])
        self.surf = self.image
        self.rect = self.surf.get_rect()
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        self.stats = Stats()
    def feed(self):
        self.stats.set_health(self.stats.get_health() + 1)
    def play(self):
        self.stats.set_happy(self.stats.get_happy() + 1)
    def love(self):
        self.stats.set_love(self.stats.get_love() + 1)
    def status(self):
        dog_status = (self.stats.get_happy(), self.stats.get_health(), self.stats.get_love())
        if all(status > 75 for status in dog_status):
            return "thriving"
        elif all(status > 50 for status in dog_status):
            return "medium"
        elif all(status > 0 for status in dog_status):
            return "bad"
    
#superclass for all loaded scenes
class Scene:
    def __init__(self, running):
        self.running = running

    def key_handler(keys):
        pass

    def loop(self):
        pass
         
class Mini_Game(Scene):
    def __init__(self, running):
       super(Mini_Game, self).__init__(running)
       self.game_list = [
           Reaction(),
       ]
       #pick a random game from the list to load
       self.game = self.game_list[random.randint(0, len(self.game_list) - 1)]
    def loop(self):
        current_scene.running = False
        self.game.loop()
        current_scene.running = True

class Reaction(Mini_Game):
    def __init__(self):
        self.font_size = 16
        self.font = pygame.font.Font('press_start.ttf', self.font_size)
        self.messages = [
            "Hit Any Key When Square Flashes",
            "Ready?",
            "Set...",
            "GO!"
        ]
    def current_time(self):
        return time.time()
    def sleep(self):
        pygame.time.wait(int(random.uniform(0.6, 3) * 1000))
    def clear_screen(self):
        screen.fill(BLACK)
    def flash(self):
        pygame.draw.rect(screen, WHITE, 
            (RESOLUTION[0]/2 - PIXEL * 50, 
            RESOLUTION[1]/2 - PIXEL * 50, 
            PIXEL * 50, PIXEL * 50)
        )
    def display_message(self, message):
        self.clear_screen()
        screen.blit(
            self.font.render(message, False, WHITE, BLACK),
            [PIXEL * 5, RESOLUTION[1]/2]
        )
    def loop(self):
        for i in range(4):
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    current_scene.current_dog.stats.exit_update()
            if i < 3:
                self.clear_screen()
                self.display_message(self.messages[i])
                pygame.display.flip()
                self.sleep()
            elif i == 3:
                self.clear_screen()
                self.flash()
                self.display_message(self.messages[i])
                pygame.display.flip()
                self.t1 = self.current_time()
                self.key_pressed = False
                while self.key_pressed == False:
                    for event in pygame.event.get():
                        if event.type == KEYDOWN:
                            self.t2 = self.current_time()
                            self.key_pressed == True
                            print("pressed")
                            break
                        elif event.type == QUIT:
                            self.running = False
                            current_scene.current_dog.stats.exit_update()
                            break
                diff = self.t2 - self.t1
                self.clear_screen()
                self.display_message("Your reaction time was {d:.2f} ms".format(d = diff*1000))
                pygame.display.flip()
                self.sleep()
                deviation = 400 - (diff*1000)
                self.clear_screen()
                if deviation > 0:
                    self.display_message("You Win!")
                    self.running = False
                else:
                    self.display_message("Try Again")
                    self.loop()
                self.sleep()
#home class handles rendering and input for main game screen
class Home(Scene):
    def __init__(self, running):
        #when home object is created, load home scene
        super(Home, self).__init__(running)
        #create dog with default picture 1
        self.current_dog = Dog(1)
        #create main menu for interacting with the dog
        self.main_menu = Menu(20, WHITE, None, ["Feed (F)", "Play (P)", "Love (L)"])
        self.sub_menu = None
        #create HUD to display dog stats
        self.hud = HUD(self.current_dog)
        #flags control game state
        self.flags = {
            "main_menu": True,
            "sub_menu": False,
            "feed": False,
            "play": False,
            "love": False,
            "overlay": False,
            "mini_game": False
        }
        self.selected_item = 0
        #if returning user, determine new dog stats from idle time
        self.current_dog.stats.instance_update()
        #check to see if dog has poor status, and update overlays accordingly
        self.overlay = Overlay(None)
        if self.current_dog.status() == "medium":
            self.overlay.stinky()
            self.flags['overlay'] = True
        elif self.current_dog.status() == "bad":
            self.overlay.sadness()
            self.flags['overlay'] = True

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
            #once sub-menu item is selected, play minigame, update stats and hud accordingly and clear menu
            if key == K_RETURN:
                self.mini_game = Mini_Game(True)
                self.running = False
                self.mini_game.loop()
                if self.flags['feed']:
                    self.current_dog.feed()
                elif self.flags['play']:
                    self.current_dog.play()
                elif self.flags['love']:
                    self.current_dog.love()
                self.hud.update(self.current_dog)
                self.clear_flags()
    #clear every stat-related flag
    def clear_flags(self):
        for flag in self.flags:
            if flag != "main_menu" and flag != "overlay":
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
            #if an overlay is flagged, draw it and update the overlay accordingly
            if self.flags['overlay']:
                self.overlay.draw(screen)
                if self.current_dog.status() == "medium":
                    self.overlay.sadness()
                elif self.current_dog.status() == "bad":
                    self.overlay.stinky()
                elif self.current_dog.status() == "thriving":
                    self.flags['overlay'] = False
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
                    [ self.hud.ideal_stat_size.get_width() * (i * 2) + PIXEL * 10,
                    ( PIXEL * 10) 
                    ])
                screen.blit(
                    self.hud.surfaces[i][1],
                    [ self.hud.ideal_stat_size.get_width() * (i * 2) + PIXEL * 15,
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
            #set framerate to 24fps
            clock.tick(24)


#initialize pygame module
pygame.init()
#define screen size
RESOLUTION = (500,500)
#define pixel size aka grid size for object placement on screen
PIXEL = RESOLUTION[0] / 100
screen = pygame.display.set_mode(RESOLUTION)
#define runtime clock
clock = pygame.time.Clock()
#define colors
BLACK = (0,0,0)
WHITE = (255,255,255)
#load home scene and call its main render loop
current_scene = Home(True)
current_scene.loop()


#once main loop exits, close game
pygame.quit()

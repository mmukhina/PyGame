
import pygame
from pygame.locals import *
import pyautogui
import sys
import time
from pygame import mixer
import random
import serial
import serial.tools.list_ports
import sqlite3
from pygame_functions import *


class Dino(pygame.sprite.Sprite):

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Dino.image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(-2500, 4300)
        self.rect.y = random.randint(-2300, 3300)

    def update(self, x, y, bullet):
        self.rect = self.rect.move(x, y)

        if pygame.sprite.spritecollide(self, bullet, True):
            self.kill()
            a = 1
        else:
            a = 0


        


class Shooting_bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction, *group):
        super().__init__(*group)
        radius = 4
        self.image = pygame.Surface((2 * radius, 2 * radius),pygame.SRCALPHA, 32)
        
        pygame.draw.circle(self.image, pygame.Color("grey"), (radius, radius), radius)
        
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        self.rect.x = x 
        self.rect.y = y
        self.direction = direction
        self.count = 0

    def update(self, move):
        
        if self.direction in ["down", "down stop"]:
            self.rect = self.rect.move(0, 5)
        elif self.direction in ["up", "up stop"]:
            self.rect = self.rect.move(0, -5)
        elif self.direction in ["left", "left stop"]:
            self.rect = self.rect.move(-5, 0)
        elif self.direction in ["right", "right stop"]:
            self.rect = self.rect.move(5, 0)

        if move == "down":
            self.rect = self.rect.move(0, -1.5)
        elif move == "up":
            self.rect = self.rect.move(0, 1.5)
        elif move == "left":
            self.rect = self.rect.move(1.5, 0)
        elif move == "right":
            self.rect = self.rect.move(-1.5, 0)

        self.count += 1

        if self.count == 60:
            self.kill()
         

            


class Bullet(pygame.sprite.Sprite):
    image = pygame.image.load("pictures/bullets_pile.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Bullet.image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(-5700, 7600)
        self.rect.y = random.randint(-4500, 5700)

    def update(self, direction, pick, player):

        if (pygame.sprite.spritecollideany(self, player) and pick == 1):
            self.rect.x = random.randint(950, 1000)
            self.rect.y = random.randint(950, 1000)
            #self.rect.x = random.randint(-2500, 4300)
            #self.rect.y = random.randint(-2300, 3300)

        if direction == "down":
            self.rect = self.rect.move(0, -1.5)
        elif direction == "up":
            self.rect = self.rect.move(0, 1.5)
        elif direction == "left":
            self.rect = self.rect.move(1.5, 0)
        elif direction == "right":
            self.rect = self.rect.move(-1.5, 0)



class Map(pygame.sprite.Sprite):
    def __init__(self, img, width, height, *group):
        super().__init__(*group)
        self.image = img

        self.rect = self.image.get_rect()
        self.rect.x = (width // 2) - (self.image.get_width() // 2)
        self.rect.y = (height // 2) - (self.image.get_height() // 2)

    def update(self, direction):
        if direction == "down":
            self.rect = self.rect.move(0, -1.5)
        elif direction == "up":
            self.rect = self.rect.move(0, 1.5)
        elif direction == "left":
            self.rect = self.rect.move(1.5, 0)
        elif direction == "right":
            self.rect = self.rect.move(-1.5, 0)
        




class Player(pygame.sprite.Sprite):
    def __init__(self, width, height, down, left, right, up, *group):
        super().__init__(*group)
        self.player_down = down
        self.player_up = up
        self.player_left = left
        self.player_right = right
        
        self.index = 0
        self.image = self.player_down[self.index]
 
        self.rect = self.image.get_rect()
        self.rect.x = (width // 2) - 30
        self.rect.y = (height // 2) - 30
 
    def update(self, direction):
        if direction == "down":
            if self.index >= len(self.player_down) * 10:
                self.index = 0
            self.image = self.player_down[self.index // 10]
        
        elif direction == "up":
            if self.index >= len(self.player_up) * 10:
                self.index = 0
            self.image = self.player_up[self.index // 10]

        elif direction == "left":
            if self.index >= len(self.player_left) * 10:
                self.index = 0
            self.image = self.player_left[self.index // 10]
            

        elif direction == "right":
            if self.index >= len(self.player_right) * 10:
                self.index = 0
            self.image = self.player_right[self.index // 10]

        elif direction == "down stop":
            self.image = self.player_down[0]

        elif direction == "left stop":
            self.image = self.player_left[0]

        elif direction == "right stop":
            self.image = self.player_right[0]

        elif direction == "up stop":
            self.image = self.player_up[0]

        self.index += 1
            

        

    

class Game():
    def __init__(self):
        self.stage = 1
        self.sound_state = 1
        
        while True:
            if self.stage == 1:
                self.start()
                
            elif self.stage == 2:
                self.main()
                    
            elif self.stage == 3:
                self.pause()


    
    def main(self):
        pygame.display.set_caption('Last Monday')
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.mixer.pre_init(44100, -16, 1, 512)
        
        self.floor_cordx = self.width // 2
        self.floor_cordy = self.height // 2

        Map(self.floor, self.width, self.height, self.map_group)

        Player(self.width, self.height, self.player_down, self.player_left, self.player_right, self.player_up, self.player_group)

        for i in range(10):
            Bullet(self.bullets_group)
        
        pygame.display.update()

        #self.clock = pygame.time.Clock()

        while self.main_game_running:
            
            if self.joystick != 1:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.running = False
                        break

                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            self.stage = 3
                            return
                        
                        if event.key == pygame.K_e:
                            self.pick = 1

                        if event.key == pygame.K_SPACE and self.no_bullet > 0:
                            self.no_bullet -= 1
                            Shooting_bullet((self.width // 2), (self.height // 2), self.direction,  self.shooting_bullet_group)

                        if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.direction = "down"
                        elif event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.direction = "up"
                        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            self.direction = "left"
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            self.direction = "right"

                    if event.type == pygame.KEYUP:
                        if (event.key == pygame.K_DOWN or event.key == pygame.K_s)  and self.direction == "down":
                            self.direction = "down stop"
                        elif (event.key == pygame.K_UP or event.key == pygame.K_w)  and self.direction == "up":
                            self.direction = "up stop"
                        elif (event.key == pygame.K_LEFT or event.key == pygame.K_a)  and self.direction == "left":
                            self.direction = "left stop"
                        elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d)  and self.direction == "right":
                            self.direction = "right stop"

                        if event.key == pygame.K_e:
                            self.pick = 0

                if self.direction == "down":
                    self.floor_cordy -= self.speed
                elif self.direction == "up":
                    self.floor_cordy += self.speed
                elif self.direction == "left":
                    self.floor_cordx += self.speed
                elif self.direction == "right":
                    self.floor_cordx -= self.speed

                self.update()
                

            else:
                self.joystick_movement()

                if self.joy_move in [b'1D\n', b'1U\n', b'1L\n', b'1R\n', b'1N\n']:
                    pygame.quit()
                    self.stage = 3
                    break


    def joystick_movement(self):
        try:
            data = self.arduino.readline()
        except Exception:
            data = b'1N\n'
            self.arduino.close()
            
        if data != b'' and data != b'5N\n':
            self.joy_move = data
            #self.sound[0].play(-1)
            #self.walking_sound = 0
        elif data != b'':
            self.joy_move = data
            #self.sound[0].stop()
            #self.walking_sound = 1
            
                

    def update(self):
        self.screen.fill((0,0,0))
        #self.floor_rect.center = self.floor_cordx, self.floor_cordy
        #self.screen.blit(self.floor, self.floor_rect)

        self.map_group.draw(self.screen)
        self.map_group.update(self.direction)

        s = pygame.Surface((self.width, 50))
        s.set_alpha(128)                
        s.fill((255,255,255))           
        self.screen.blit(s, (0,0))

        for i in range(self.health):
            self.screen.blit(self.heart, [10 + i * 40, 10])

        self.screen.blit(self.bullet, [300, 10])

        font1 = pygame.font.SysFont('comicsansms',19)
        temp = "X " + str(self.no_bullet)
        text = font1.render(temp, True , (0,0,0))
        self.screen.blit(text , (350, 11))

        self.screen.blit(self.monster, [500, 10])
        text = font1.render(str(self.no_killed), True , (0,0,0))
        self.screen.blit(text , (550, 11))

        temp = str(self.floor_cordx) + " " + str(self.floor_cordy)
        text = font1.render(temp, True , (0,0,0))
        self.screen.blit(text , (700, 10))

        self.player_group.draw(self.screen)
        self.player_group.update(self.direction)

        pick_up = pygame.sprite.groupcollide(self.player_group, self.bullets_group, False, False)
        if pick_up != {} and self.pick == 1:
            self.no_bullet += (len(pick_up[list(pick_up.keys())[0]]) * 5)


        self.bullets_group.draw(self.screen)
        self.bullets_group.update(self.direction, self.pick, self.player_group)

        self.shooting_bullet_group.draw(self.screen)
        self.shooting_bullet_group.update(self.direction)
        
        pygame.display.update()
        #self.clock.tick(50)

    def load(self):

        self.width, self.height = pyautogui.size()

        self.floor = pygame.image.load('pictures/map7.jpg')
        self.heart = pygame.image.load("pictures/heart.png")
        self.bullet = pygame.image.load("pictures/bullet.png")
        self.monster = pygame.image.load("pictures/monster.png")

        self.keys = [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_d, pygame.K_s, pygame.K_a]

        self.joy_move = b''
        self.direction = "None"

        self.health = 5
        self.no_bullet = 0
        self.no_killed = 0
        self.pick = 0
        self.shoot = 0

        # Sprite группы
        self.player_group = pygame.sprite.Group()
        self.bullets_group = pygame.sprite.Group()
        self.dino_group = pygame.sprite.Group()
        self.shooting_bullet_group = pygame.sprite.Group()
        self.border_group = pygame.sprite.Group()
        self.map_group = pygame.sprite.Group()

        self.main_game_running = 1

        con = sqlite3.connect("database.db")
        cur = con.cursor()

        result = cur.execute("""SELECT * FROM Lists WHERE key is "player_down" """).fetchall()
        self.player_down = [pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute("""SELECT * FROM Lists WHERE key is "player_up" """).fetchall()
        self.player_up = [pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute("""SELECT * FROM Lists WHERE key is "player_left" """).fetchall()
        self.player_left = [pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute("""SELECT * FROM Lists WHERE key is "player_right" """).fetchall()
        self.player_right = [pygame.image.load(i) for i in result[0][1:] if i != "no"]

        con.close()

        
                

    def pause(self):
        pygame.init()
        pygame.display.set_caption('Last Monday')
        pygame.display.set_icon(pygame.image.load("pictures/icon.ico"))
        self.screen_start = pygame.display.set_mode((self.w, self.h))

        con = sqlite3.connect("database.db")
        cur = con.cursor()

        result = cur.execute("""SELECT * FROM Lists WHERE key is "pause_window" """).fetchall()
        self.pause_window = [pygame.image.load(i) for i in result[0][1:] if i != "no"]

        con.close()

        mixer.music.load("Sound/background1.mp3")
        mixer.music.play(-1)

        count = 0

        color_dark = (0,0,0)
          
        font1 = pygame.font.SysFont('comicsansms',23)
          
        text = font1.render('Продолжить игру' , True , (255,255,255))
        text2 = font1.render('Подключить джойстик' , True , (255,255,255))
        text3 = font1.render('Подключить джойстик' , True , (26, 199, 73))
        text4 = font1.render('Подключить джойстик' , True , (237, 0, 0))
        text5 = font1.render('Меню' , True , (255, 255, 255))

        pygame.display.update()

        while self.start_running:
            if count % 1000 == 0:
                self.screen_start.blit(self.pause_window[random.randint(0, 4)], [0, 0])

            count += 1

            if self.sound_state == 2:
                self.screen_start.blit(self.sound_image1 , (10, 10))
                mixer.music.play(-1)
                self.sound_state = 1
            elif self.sound_state == 0:
                self.screen_start.blit(self.sound_image2 , (10, 10))
                mixer.music.stop()
            else:
                self.screen_start.blit(self.sound_image1 , (10, 10))

            mouse = pygame.mouse.get_pos()

            # Кнопка 1
            if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and self.h * 0.62 <= mouse[1] <= self.h * 0.62 + 50:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.62 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.62 ,300,50], 1, border_radius = 10)
                  
            else:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.62 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.62 ,300,50], 2, border_radius = 10)


            # Кнопка 2
            if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and self.h * 0.72 <= mouse[1] <= self.h * 0.7 + 50:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.72 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.72 ,300,50], 1, border_radius = 10)
                  
            else:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.72 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.72 ,300,50], 2, border_radius = 10)

            self.screen_start.blit(text , (self.w * 0.57 + 54, self.h * 0.72 + 5))
            
            # Кнопка 3
            if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and self.h * 0.82 <= mouse[1] <= self.h * 0.82 + 50:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.82 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.82 ,300,50], 1, border_radius = 10)
                  
            else:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.82 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.82 ,300,50], 2, border_radius = 10)
                
            self.screen_start.blit(text5 , (self.w * 0.57 + 115, self.h * 0.82 + 5))
                

            if self.joystick == 1:
                self.screen_start.blit(text3 , (self.w * 0.57 + 21, self.h * 0.62 + 5))
            elif self.joystick == 0:
                self.screen_start.blit(text4 , (self.w * 0.57 + 21, self.h * 0.62 + 5))
            else:
                self.screen_start.blit(text2 , (self.w * 0.57 + 21, self.h * 0.62 + 5))
                

            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.stop = 1
                    self.start_running = False
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.w * 0.6 <= mouse[0] <= self.w * 0.6 + 180 and self.h * 0.72 <= mouse[1] <= self.h * 0.72 + 50:
                        self.stage = 2
                        pygame.quit()

                    elif self.w * 0.6 <= mouse[0] <= self.w * 0.6 + 180 and self.h * 0.82 <= mouse[1] <= self.h * 0.82 + 50:
                        self.stage = 1
                        pygame.quit()
                        return

                    elif 10 <= mouse[0] <= 50 and 10 <= mouse[1] <= 50 and self.sound_state == 1:
                        self.sound_state = 0

                    elif 10 <= mouse[0] <= 50 and 10 <= mouse[1] <= 50 and self.sound_state == 0:
                        self.sound_state = 2

                    elif self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and self.h * 0.62 <= mouse[1] <= self.h * 0.62 + 50:
                        if self.joystick_connect() == 1:
                            self.joystick = 1
                            time.sleep(2)
                            self.arduino.write(bytes("1", 'utf-8'))
                            self.speed = 1.5
                        else:
                            self.joystick = 0
                            pyautogui.alert("Джойстик не найден")
                            self.speed = 1.5
        


    def start(self):
        pygame.init()
        self.w = 900
        self.h = 700

        con = sqlite3.connect("database.db")
        cur = con.cursor()

        result = cur.execute("""SELECT * FROM Lists WHERE key is "first_window" """).fetchall()
        self.first_window = [pygame.image.load(i) for i in result[0][1:] if i != "no"]

        con.close()

        self.sound_image1 = pygame.image.load("pictures/sound1.png")
        self.sound_image2 = pygame.image.load("pictures/sound2.png")

        self.loading_image = pygame.image.load("pictures/loading.jpg")
        
        pygame.display.set_caption('Last Monday')
        pygame.display.set_icon(pygame.image.load("pictures/icon.ico"))
        self.screen_start = pygame.display.set_mode((self.w, self.h))
        self.start_running = 1
        
        self.joystick = 3
        self.speed = 1.5
        return_to_main = 0

        mixer.music.load("Sound/background1.mp3")
        mixer.music.play(-1)

        count = 0

        color_dark = (0,0,0)
          
        font1 = pygame.font.SysFont('comicsansms',23)
          
        text = font1.render('Начать игру' , True , (255,255,255))
        text2 = font1.render('Подключить джойстик' , True , (255,255,255))
        text3 = font1.render('Подключить джойстик' , True , (26, 199, 73))
        text4 = font1.render('Подключить джойстик' , True , (237, 0, 0))
        text5 = font1.render('Закрыть игру' , True , (255, 255, 255))

        pygame.display.update()

        while self.start_running:
            if count % 1000 == 0:
                self.screen_start.blit(self.first_window[random.randint(0, 4)], [0, 0])

            count += 1

            if self.sound_state == 2:
                self.screen_start.blit(self.sound_image1 , (10, 10))
                mixer.music.play(-1)
                self.sound_state = 1
            elif self.sound_state == 0:
                self.screen_start.blit(self.sound_image2 , (10, 10))
                mixer.music.stop()
            else:
                self.screen_start.blit(self.sound_image1 , (10, 10))

            mouse = pygame.mouse.get_pos()

            # Кнопка 1
            if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and self.h * 0.62 <= mouse[1] <= self.h * 0.62 + 50:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.62 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.62 ,300,50], 1, border_radius = 10)
                  
            else:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.62 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.62 ,300,50], 2, border_radius = 10)


            # Кнопка 2
            if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and self.h * 0.72 <= mouse[1] <= self.h * 0.7 + 50:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.72 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.72 ,300,50], 1, border_radius = 10)
                  
            else:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.72 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.72 ,300,50], 2, border_radius = 10)

            self.screen_start.blit(text , (self.w * 0.57 + 85, self.h * 0.72 + 5))
            
            # Кнопка 3
            if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and self.h * 0.82 <= mouse[1] <= self.h * 0.82 + 50:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.82 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.82 ,300,50], 1, border_radius = 10)
                  
            else:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.82 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.82 ,300,50], 2, border_radius = 10)
                
            self.screen_start.blit(text5 , (self.w * 0.57 + 75, self.h * 0.82 + 5))
                

            if self.joystick == 1:
                self.screen_start.blit(text3 , (self.w * 0.57 + 21, self.h * 0.62 + 5))
            elif self.joystick == 0:
                self.screen_start.blit(text4 , (self.w * 0.57 + 21, self.h * 0.62 + 5))
            else:
                self.screen_start.blit(text2 , (self.w * 0.57 + 21, self.h * 0.62 + 5))
                

            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.stop = 1
                    self.start_running = False
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.w * 0.6 <= mouse[0] <= self.w * 0.6 + 180 and self.h * 0.72 <= mouse[1] <= self.h * 0.72 + 50:
                        self.screen_start.blit(self.loading_image , (0, 0))
                        self.stage = 2
                        pygame.display.update()
                        self.load()
                        pygame.quit()
                        return

                    elif self.w * 0.6 <= mouse[0] <= self.w * 0.6 + 180 and self.h * 0.82 <= mouse[1] <= self.h * 0.82 + 50:
                        pygame.quit()
                        sys.exit()

                    elif 10 <= mouse[0] <= 50 and 10 <= mouse[1] <= 50 and self.sound_state == 1:
                        self.sound_state = 0

                    elif 10 <= mouse[0] <= 50 and 10 <= mouse[1] <= 50 and self.sound_state == 0:
                        self.sound_state = 2

                    elif self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and self.h * 0.62 <= mouse[1] <= self.h * 0.62 + 50:
                        if self.joystick_connect() == 1:
                            self.joystick = 1
                            time.sleep(2)
                            self.arduino.write(bytes("1", 'utf-8'))
                            self.speed = 1.5
                        else:
                            self.joystick = 0
                            pyautogui.alert("Джойстик не найден")
                            self.speed = 1.5
        
                            

    def findArduinoUnoPort(self):
        portList = list(serial.tools.list_ports.comports())
        for port in portList:
            if ("VID:PID=2341:0043" in port[0] or
                "VID:PID=2341:0043" in port[1] or
               "VID:PID=2341:0043" in port[2]):
                    return port[0]


    def joystick_connect(self):
        try:
            self.arduino.close()
            unoPort = True
        except Exception:
            unoPort = self.findArduinoUnoPort()
        if unoPort:
            try:
                self.arduino = serial.Serial(port='COM5', baudrate=9600,timeout=0.1)
                return 1

            except Exception:
                return 0

        return 0
        
        

    def again(self):
        return self.stop
        


if __name__ == '__main__':
    ex = Game()

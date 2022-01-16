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


class Spider(pygame.sprite.Sprite):
    image = pygame.image.load("pictures/spider.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Spider.image
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

        with open('bullets.txt', 'a') as f:
            f.write(str(a))

        


class Shooting_bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction, *group):
        super().__init__(*group)
        radius = 7
        self.image = pygame.Surface((2 * radius, 2 * radius),pygame.SRCALPHA, 32)
        
        pygame.draw.circle(self.image, pygame.Color("black"), (radius, radius), radius)
        
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        self.rect.x = x 
        self.rect.y = y
        self.direction = direction
        self.count = 0

    def update(self, x, y, spider):
        
        if self.direction == 0:
            self.rect = self.rect.move(0, - 10)
        elif self.direction == 180:
            self.rect = self.rect.move(0, 10)
        elif self.direction == 270:
            self.rect = self.rect.move(10, 0)
        elif self.direction == 90:
            self.rect = self.rect.move(-10, 0)

        self.rect = self.rect.move(x, y)
        self.count += 1

        if self.count == 50:
            self.kill()
         

            


class Bullet(pygame.sprite.Sprite):
    image = pygame.image.load("pictures/bullets_pile.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Bullet.image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(-2500, 4300)
        self.rect.y = random.randint(-2300, 3300)

    def update(self, x, y,horizontal_borders, vertical_borders, e):

        if (pygame.sprite.spritecollideany(self, horizontal_borders) or pygame.sprite.spritecollideany(self, vertical_borders)) and e == 1:
            self.rect.x = random.randint(-2500, 4300)
            self.rect.y = random.randint(-2300, 3300)
            a = 1
        else:
            a = 0

        self.rect = self.rect.move(x, y)
        with open('bullets.txt', 'a') as f:
            f.write(str(a))




class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2,horizontal_borders, vertical_borders):
        super().__init__(horizontal_borders, vertical_borders)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


    

class Game():
    def __init__(self):
        pygame.init()
        self.stop = 0
        self.stage = 1
        self.running = True

        self.width, self.height = pyautogui.size()
        self.w = 900
        self.h = 700

        self.floor = pygame.image.load('pictures/map5.png')
        self.char = pygame.image.load("pictures/char.png")
        self.heart = pygame.image.load("pictures/heart.png")
        self.bullet = pygame.image.load("pictures/bullet.png")
        self.monster = pygame.image.load("pictures/monster.png")
        
        self.player_cordx = self.width // 2 
        self.player_cordy = self.height // 2
        self.floor_cordx = self.width // 2
        self.floor_cordy = self.height // 2

        self.floor_rect = self.floor.get_rect()
        self.floor_rect.center = self.floor_cordx, self.floor_cordy

        self.player_rect = self.char.get_rect()
        self.player_rect.center = self.player_cordx, self.player_cordy
        self.rotation = 0
        self.clock = pygame.time.Clock()

        self.sound_image1 = pygame.image.load("pictures/sound1.png")
        self.sound_image2 = pygame.image.load("pictures/sound2.png")

        con = sqlite3.connect("database.db")
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM Lists WHERE key is "sound" """).fetchall()
        self.sound = [pygame.mixer.Sound(i) for i in result[0][1:] if i != "no"]

        result = cur.execute("""SELECT * FROM Lists WHERE key is "first_window" """).fetchall()
        self.first_window = [pygame.image.load(i) for i in result[0][1:] if i != "no"]

        self.walking_sound = 1

        self.keys = [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_d, pygame.K_s, pygame.K_a]

        self.joy_move = b''

        self.cordx = 0
        self.cordy = 0

        self.health = 5
        self.no_bullet = 0

        self.no_killed = 0

        self.bullet_image = pygame.image.load("pictures/bullets_pile.png")

        self.bullets_group = pygame.sprite.Group()
        self.spider_group = pygame.sprite.Group()

        self.default = 1

        self.bullet_move_x = 0
        self.bullet_move_y = 0

        self.horizontal_borders = pygame.sprite.Group()
        self.vertical_borders = pygame.sprite.Group()

        self.shooting_bullet_group = pygame.sprite.Group()

        self.e_pressed = 0

        self.level = 2



        while self.running:
            if self.stage == 1:
                self.start()
                if self.stop == 1:
                    sys.exit()
                    
                self.stage = 2
                self.running = True
                
            elif self.stage == 2:
                self.main()

                if self.default:
                    for _ in range(10):
                        Bullet(self.bullets_group)

                    for _ in range(10):
                        Spider(self.spider_group)


                    Border(self.width // 2 - 25, self.height // 2 - 25, self.width // 2 + 25, self.height // 2 + 25, self.horizontal_borders, self.vertical_borders)
                    Border(self.width // 2 + 25, self.height // 2 - 25, self.width // 2 + 25, self.height // 2 + 25, self.horizontal_borders, self.vertical_borders)
                    Border(self.width // 2 - 25, self.height // 2 - 25, self.width // 2 - 25, self.height // 2 + 25, self.horizontal_borders, self.vertical_borders)
                    Border(self.width // 2 - 25, self.height // 2 + 25, self.width // 2 + 25, self.height // 2 + 25, self.horizontal_borders, self.vertical_borders)

                    self.default = 0
                    self.bullets_group.draw(self.screen)
                    self.spider_group.draw(self.screen)
                    self.horizontal_borders.draw(self.screen)
                    self.vertical_borders.draw(self.screen)

                    
                    
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.running = False
                        break

                    if self.joystick != 1:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                pygame.quit()
                                self.stage = 3
                                break

                            if event.key in self.keys and self.walking_sound == 1 and self.sound_state == 1:
                                self.sound[0].play(-1)
                                self.walking_sound = 0


                            if event.key == pygame.K_e:
                                self.e_pressed = 1
                            else:
                                self.e_pressed = 0

                            if event.key == pygame.K_SPACE and self.no_bullet > 0:
                                Shooting_bullet(self.player_cordx, self.player_cordy, self.rotation, self.shooting_bullet_group)
                                self.shooting_bullet_group.draw(self.screen)
                                self.no_bullet -= 1
                                    


                        if event.type == pygame.KEYUP:
                            if event.key in self.keys:
                                self.sound[0].stop()
                                self.walking_sound = 1
                                self.bullet_move_x = 0
                                self.bullet_move_y = 0

                                
                        self.movement()
                        
                        self.update()


                    else:
                        self.joystick_movement()

                        if self.joy_move in [b'1D\n', b'1U\n', b'1L\n', b'1R\n', b'1N\n']:
                            pygame.quit()
                            self.stage = 3
                            break


            elif self.stage == 3:
                self.cont()
                if self.stop == 1:
                    sys.exit()
                self.stage = 2
                self.running = True


    def update(self):
        
        self.floor_rect.center = self.floor_cordx, self.floor_cordy
        self.screen.blit(self.floor, self.floor_rect)

        self.bullets_group.draw(self.screen)
        self.bullets_group.update(self.bullet_move_x ,self.bullet_move_y,self.horizontal_borders, self.vertical_borders, self.e_pressed) 
        
        with open ("bullets.txt", "r") as myfile:
            data = myfile.read().splitlines()

        if "1" in data[0]:
            self.no_bullet += 5

        open("bullets.txt", "w").close()

        self.spider_group.draw(self.screen)
        self.spider_group.update(self.bullet_move_x ,self.bullet_move_y, self.shooting_bullet_group)

        self.shooting_bullet_group.draw(self.screen)
        self.shooting_bullet_group.update(self.bullet_move_x ,self.bullet_move_y, self.spider_group)

        with open ("bullets.txt", "r") as myfile:
            data = myfile.read().splitlines()

        if "1" in data[0]:
            self.no_killed += 1

            for _ in range(self.level):
                Spider(self.spider_group)

            self.bullets_group.draw(self.screen)
            self.spider_group.update(self.bullet_move_x ,self.bullet_move_y, self.shooting_bullet_group)

            self.level += 1

        open("bullets.txt", "w").close()

        self.horizontal_borders.draw(self.screen)
        self.vertical_borders.draw(self.screen)

        self.player_rect.center = self.player_cordx, self.player_cordy
        self.screen.blit(self.char, self.player_rect)

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

        

        
        pygame.display.update()

    def zero_pos(self):
        self.bullet_move_x = 0
        self.bullet_move_y = 0

                

    def joystick_movement(self):
        try:
            data = self.arduino.readline()
        except Exception:
            data = b'1N\n'
            self.arduino.close()
            
        if data != b'' and data != b'5N\n' and self.walking_sound == 1:
            self.joy_move = data
            self.sound[0].play(-1)
            self.walking_sound = 0
        elif data != b'':
            self.joy_move = data
            self.sound[0].stop()
            self.walking_sound = 1
            
        if self.joy_move in [b'5D\n', b'2D\n', b'3D\n', b'4D\n']:
            if self.floor_cordy <= -2420 and self.player_cordy <= 1050 and self.player_cordy >= self.height // 2:
                self.player_cordy += self.speed
            elif self.floor_cordy >= -2420 and self.player_cordy == self.height // 2:
                self.floor_cordy -= self.speed 
            elif self.player_cordy <= self.height // 2:
                self.player_cordy += self.speed 

            self.char = pygame.transform.rotate(self.char, abs(360 - self.rotation + 180))
            self.rotation = 180


        elif self.joy_move in [b'5U\n', b'2U\n', b'3U\n', b'4U\n']:
            if self.floor_cordy >= 3500 and self.player_cordy >= 30 and self.player_cordy <= self.height // 2:
                self.player_cordy -= self.speed
            elif self.floor_cordy <= 3500 and self.player_cordy == self.height // 2:
                self.floor_cordy += self.speed
            elif self.player_cordy >= self.height // 2:
                self.player_cordy -= self.speed

            self.char = pygame.transform.rotate(self.char, abs(360 - self.rotation))
            self.rotation = 0
          
        elif self.joy_move in [b'5L\n', b'2L\n', b'3L\n', b'4L\n']:
            if self.floor_cordx >= 4500 and self.player_cordx >= 30 and self.player_cordx <= self.width // 2:
                self.player_cordx -= self.speed
            elif self.floor_cordx <= 4500 and self.player_cordx == self.width // 2:
                self.floor_cordx += self.speed
            elif self.player_cordx >= self.width // 2:
                self.player_cordx -= self.speed

            self.char = pygame.transform.rotate(self.char, abs(360 - self.rotation + 90))
            self.rotation = 90
                
        elif self.joy_move in [b'5R\n', b'2R\n', b'3R\n', b'4R\n']:
            if self.floor_cordx <= -2580 and self.player_cordx <= 1890 and self.player_cordx >= self.width // 2:
                self.player_cordx += self.speed
            elif self.floor_cordx >= -2580 and self.player_cordx == self.width // 2:
                self.floor_cordx -= self.speed
            elif self.player_cordx <= self.width // 2:
                self.player_cordx += self.speed

            self.char = pygame.transform.rotate(self.char, abs(360 - self.rotation + 270))
            self.rotation = 270


    def movement(self):
        
        keys = pygame.key.get_pressed()

        if keys[K_DOWN] or keys[K_s]:
            if self.floor_cordy <= -2400 and self.player_cordy <= 1020 and self.player_cordy >= self.height // 2:
                self.player_cordy += self.speed
                
                self.bullet_move_x = 0
                self.bullet_move_y = self.speed
                    
            elif self.floor_cordy >= -2400 and self.player_cordy == self.height // 2:
                self.floor_cordy -= self.speed
                
                self.bullet_move_x = 0
                self.bullet_move_y = -1 * self.speed
                    
            elif self.player_cordy <= self.height // 2:
                self.player_cordy += self.speed
                
                self.bullet_move_x = 0
                self.bullet_move_y = self.speed

            self.cordy -= 1

            self.char = pygame.transform.rotate(self.char, abs(360 - self.rotation + 180))
            self.rotation = 180

        elif keys[K_UP] or keys[K_w]:
            if self.floor_cordy >= 3480 and self.player_cordy >= 50 and self.player_cordy <= self.height // 2:
                self.player_cordy -= self.speed

                self.bullet_move_x = 0
                self.bullet_move_y = -1 * self.speed
                    
            elif self.floor_cordy <= 3480 and self.player_cordy == self.height // 2:
                self.floor_cordy += self.speed

                self.bullet_move_x = 0
                self.bullet_move_y = self.speed
                    
            elif self.player_cordy >= self.height // 2:
                self.player_cordy -= self.speed

                self.bullet_move_x = 0
                self.bullet_move_y = -1 * self.speed

            self.cordy += 1

            self.char = pygame.transform.rotate(self.char, abs(360 - self.rotation))
            self.rotation = 0
          
        elif keys[K_LEFT] or keys[K_a]:
            if self.floor_cordx >= 4480 and self.player_cordx >= 50 and self.player_cordx <= self.width // 2:
                self.player_cordx -= self.speed
                self.bullet_move_x = -1 * self.speed
                self.bullet_move_y = 0
            elif self.floor_cordx <= 4480 and self.player_cordx == self.width // 2:
                self.floor_cordx += self.speed
                self.bullet_move_x = self.speed
                self.bullet_move_y = 0
            elif self.player_cordx >= self.width // 2:
                self.player_cordx -= self.speed
                self.bullet_move_x = -1 * self.speed
                self.bullet_move_y = 0

            self.cordx -= 1

            self.char = pygame.transform.rotate(self.char, abs(360 - self.rotation + 90))
            self.rotation = 90
                
        elif keys[K_RIGHT] or keys[K_d]:
            if self.floor_cordx <= -2560 and self.player_cordx <= 1840 and self.player_cordx >= self.width // 2:
                self.player_cordx += self.speed
                self.bullet_move_x = self.speed
                self.bullet_move_y = 0
            elif self.floor_cordx >= -2560 and self.player_cordx == self.width // 2:
                self.floor_cordx -= self.speed
                self.bullet_move_x = -1 * self.speed
                self.bullet_move_y = 0
            elif self.player_cordx <= self.width // 2:
                self.player_cordx += self.speed
                self.bullet_move_x = self.speed
                self.bullet_move_y = 0

            self.cordx += 1

            self.char = pygame.transform.rotate(self.char, abs(360 - self.rotation + 270))
            self.rotation = 270

        else:
            self.zero_pos()

            

        """
        if count == 0:
            char = pygame.image.load("pictures/1.png")
        elif count == 25:
            char = pygame.image.load("pictures/2.png")
        elif count == 50:
            char = pygame.image.load("pictures/1.png")
        elif count == 100:
            char = pygame.image.load("pictures/3.png")

        if count < 151:
            count += 1
        else:
            count = 0"""
                    

    def cont(self):
        pygame.display.set_caption('?????')
        pygame.display.set_icon(pygame.image.load("pictures/icon.ico"))
        pygame.init()
        self.screen_start = pygame.display.set_mode((self.w, self.h))
        self.running = 1

        mixer.music.load("Sound/background1.mp3")
        mixer.music.play(-1)

        count = 0

        color_dark = (0,0,0)
          
        font1 = pygame.font.SysFont('comicsansms',23)
          
        text = font1.render('Продолжить' , True , (255,255,255))
        text2 = font1.render('Подключить джойстик' , True , (255,255,255))
        text3 = font1.render('Подключить джойстик' , True , (26, 199, 73))
        text4 = font1.render('Подключить джойстик' , True , (237, 0, 0))

        pygame.display.update()

        while self.running:
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

            if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and self.h * 0.82 <= mouse[1] <= self.h * 0.82 + 50:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.82 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.82 ,300,50], 1, border_radius = 10)
                  
            else:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.82 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.82 ,300,50], 2, border_radius = 10)
                
            self.screen_start.blit(text , (self.w * 0.57 + 80, self.h * 0.82 + 5))

            if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and self.h * 0.7 <= mouse[1] <= self.h * 0.7 + 50:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.7 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.7 ,300,50], 1, border_radius = 10)
                  
            else:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.7 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.7 ,300,50], 2, border_radius = 10)
                

            if self.joystick == 1:
                self.screen_start.blit(text3 , (self.w * 0.57 + 21, self.h * 0.7 + 5))
            elif self.joystick == 0:
                self.screen_start.blit(text4 , (self.w * 0.57 + 21, self.h * 0.7 + 5))
            else:
                self.screen_start.blit(text2 , (self.w * 0.57 + 21, self.h * 0.7 + 5))
                

            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.stop = 1
                    self.running = False
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.w * 0.6 <= mouse[0] <= self.w * 0.6 + 180 and self.h * 0.8 <= mouse[1] <= self.h * 0.8 + 50:
                        self.stop = 0
                        self.running = 0
                        pygame.quit()

                    elif 10 <= mouse[0] <= 50 and 10 <= mouse[1] <= 50 and self.sound_state == 1:
                        self.sound_state = 0

                    elif 10 <= mouse[0] <= 50 and 10 <= mouse[1] <= 50 and self.sound_state == 0:
                        self.sound_state = 2

                    elif self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and self.h * 0.7 <= mouse[1] <= self.h * 0.7 + 50:
                        if self.joystick_connect() == 1:
                            self.joystick = 1
                            time.sleep(2)
                            self.arduino.write(bytes("1", 'utf-8'))
                            self.speed = 25
                        else:
                            self.joystick = 0
                            pyautogui.alert("Джойстик не найден")
                            self.speed = 25
        


    def start(self):
        pygame.display.set_caption('?????')
        pygame.display.set_icon(pygame.image.load("pictures/icon.ico"))
        pygame.init()
        self.screen_start = pygame.display.set_mode((self.w, self.h))
        self.running = 1
        self.sound_state = 1
        self.joystick = 3
        self.speed = 25
        

        mixer.music.load("Sound/background1.mp3")
        mixer.music.play(-1)

        count = 0

        color_dark = (0,0,0)
          
        font1 = pygame.font.SysFont('comicsansms',23)
          
        text = font1.render('Начать игру' , True , (255,255,255))
        text2 = font1.render('Подключить джойстик' , True , (255,255,255))
        text3 = font1.render('Подключить джойстик' , True , (26, 199, 73))
        text4 = font1.render('Подключить джойстик' , True , (237, 0, 0))

        pygame.display.update()

        while self.running:
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

            if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and self.h * 0.82 <= mouse[1] <= self.h * 0.82 + 50:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.82 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.82 ,300,50], 1, border_radius = 10)
                  
            else:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.82 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.82 ,300,50], 2, border_radius = 10)
                
            self.screen_start.blit(text , (self.w * 0.57 + 80, self.h * 0.82 + 5))

            if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and self.h * 0.7 <= mouse[1] <= self.h * 0.7 + 50:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.7 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.7 ,300,50], 1, border_radius = 10)
                  
            else:
                pygame.draw.rect(self.screen_start, color_dark, [self.w * 0.57 ,self.h * 0.7 ,300,50], border_radius = 10)
                pygame.draw.rect(self.screen_start, (255, 255, 255), [self.w * 0.57 ,self.h * 0.7 ,300,50], 2, border_radius = 10)
                

            if self.joystick == 1:
                self.screen_start.blit(text3 , (self.w * 0.57 + 21, self.h * 0.7 + 5))
            elif self.joystick == 0:
                self.screen_start.blit(text4 , (self.w * 0.57 + 21, self.h * 0.7 + 5))
            else:
                self.screen_start.blit(text2 , (self.w * 0.57 + 21, self.h * 0.7 + 5))
                

            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.stop = 1
                    self.running = False
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.w * 0.6 <= mouse[0] <= self.w * 0.6 + 180 and self.h * 0.8 <= mouse[1] <= self.h * 0.8 + 50:
                        self.stop = 0
                        self.running = 0
                        pygame.quit()

                    elif 10 <= mouse[0] <= 50 and 10 <= mouse[1] <= 50 and self.sound_state == 1:
                        self.sound_state = 0

                    elif 10 <= mouse[0] <= 50 and 10 <= mouse[1] <= 50 and self.sound_state == 0:
                        self.sound_state = 2

                    elif self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and self.h * 0.7 <= mouse[1] <= self.h * 0.7 + 50:
                        if self.joystick_connect() == 1:
                            self.joystick = 1
                            time.sleep(2)
                            self.arduino.write(bytes("1", 'utf-8'))
                            self.speed = 25
                        else:
                            self.joystick = 0
                            pyautogui.alert("Джойстик не найден")
                            self.speed = 25
        
                            

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
        


    def main(self):
        pygame.display.set_caption('?????')
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.running = True
        pygame.mixer.pre_init(44100, -16, 1, 512)
        


if __name__ == '__main__':
    ex = Game()

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

class Game():
    def __init__(self):
        pygame.init()
        self.stop = 0
        self.stage = 1
        self.running = True

        self.width, self.height = pyautogui.size()
        self.w = 900
        self.h = 700

        self.floor = pygame.image.load('pictures/map.png')
        self.char = pygame.image.load("pictures/char.png")
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

        while self.running:
            if self.stage == 1:
                self.start()
                if self.stop == 1:
                    sys.exit()
                    
                self.stage = 2
                self.running = True
                
            elif self.stage == 2:
                self.main()

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

                            if event.key in self.keys and self.walking_sound == 1:
                                self.sound[0].play(-1)
                                self.walking_sound = 0

                        if event.type == pygame.KEYUP:
                            if event.key in self.keys:
                                self.sound[0].stop()
                                self.walking_sound = 1

                        self.movement()

                    else:
                        self.joystick_movement()

                        if self.joy_move in [b'1D\n', b'1U\n', b'1L\n', b'1R\n', b'1N\n']:
                            pygame.quit()
                            self.stage = 3
                            break

                        self.floor_rect.center = self.floor_cordx, self.floor_cordy
                        self.player_rect.center = self.player_cordx, self.player_cordy
                        self.screen.blit(self.floor, self.floor_rect)
                        self.screen.blit(self.char, self.player_rect)
                        pygame.display.update()

                    
            elif self.stage == 3:
                self.cont()
                if self.stop == 1:
                    sys.exit()
                self.stage = 2
                self.running = True
                

    def joystick_movement(self):
        try:
            data = self.arduino.readline()
        except Exception:
            data = b'1N\n'
            
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
            if self.floor_cordy <= -2420 and self.player_cordy <= 1050 and self.player_cordy >= self.height // 2:
                self.player_cordy += self.speed
            elif self.floor_cordy >= -2420 and self.player_cordy == self.height // 2:
                self.floor_cordy -= self.speed
            elif self.player_cordy <= self.height // 2:
                self.player_cordy += self.speed

            self.char = pygame.transform.rotate(self.char, abs(360 - self.rotation + 180))
            self.rotation = 180


        elif keys[K_UP] or keys[K_w]:
            if self.floor_cordy >= 3500 and self.player_cordy >= 30 and self.player_cordy <= self.height // 2:
                self.player_cordy -= self.speed
            elif self.floor_cordy <= 3500 and self.player_cordy == self.height // 2:
                self.floor_cordy += self.speed
            elif self.player_cordy >= self.height // 2:
                self.player_cordy -= self.speed

            self.char = pygame.transform.rotate(self.char, abs(360 - self.rotation))
            self.rotation = 0
          
        elif keys[K_LEFT] or keys[K_a]:
            if self.floor_cordx >= 4500 and self.player_cordx >= 30 and self.player_cordx <= self.width // 2:
                self.player_cordx -= self.speed
            elif self.floor_cordx <= 4500 and self.player_cordx == self.width // 2:
                self.floor_cordx += self.speed
            elif self.player_cordx >= self.width // 2:
                self.player_cordx -= self.speed

            self.char = pygame.transform.rotate(self.char, abs(360 - self.rotation + 90))
            self.rotation = 90
                
        elif keys[K_RIGHT] or keys[K_d]:
            if self.floor_cordx <= -2580 and self.player_cordx <= 1890 and self.player_cordx >= self.width // 2:
                self.player_cordx += self.speed
            elif self.floor_cordx >= -2580 and self.player_cordx == self.width // 2:
                self.floor_cordx -= self.speed
            elif self.player_cordx <= self.width // 2:
                self.player_cordx += self.speed

            self.char = pygame.transform.rotate(self.char, abs(360 - self.rotation + 270))
            self.rotation = 270

        self.floor_rect.center = self.floor_cordx, self.floor_cordy
        self.player_rect.center = self.player_cordx, self.player_cordy
        self.screen.blit(self.floor, self.floor_rect)
        self.screen.blit(self.char, self.player_rect)
        pygame.display.update()

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
                            self.speed = 5
        


    def start(self):
        pygame.display.set_caption('?????')
        pygame.display.set_icon(pygame.image.load("pictures/icon.ico"))
        pygame.init()
        self.screen_start = pygame.display.set_mode((self.w, self.h))
        self.running = 1
        self.sound_state = 1
        self.joystick = 3
        self.speed = 5

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
                            self.speed = 5
        
                            

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

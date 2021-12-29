import pygame
from pygame.locals import *
import pyautogui

def open_start():
    w, h = 900, 700
    pygame.init()
    screen_start = pygame.display.set_mode((w, h))
    running = 1
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = 0

    pygame.quit()

def open_stop():
    w, h = 900, 700
    pygame.init()
    screen_start = pygame.display.set_mode((w, h))
    running = 1
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                pygame.quit
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = 0
                print("hiii")
                return 0

    
    


open_start()


width, height = pyautogui.size()
pygame.init()
screen = pygame.display.set_mode((width, height))
running = True

floor = pygame.image.load('pictures/map.png')
char = pygame.image.load("pictures/char.png")
player_cordx = width // 2 
player_cordy = height // 2
floor_cordx = width // 2
floor_cordy = height // 2

floor_rect = floor.get_rect()
floor_rect.center = floor_cordx, floor_cordy

player_rect = char.get_rect()
player_rect.center = player_cordx, player_cordy
rotation = 0
speed = 5
count = 0

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    if open_start() == 0:
                        print("hi")
                    else:
                        pygame.quit()

    keys = pygame.key.get_pressed()

    if keys[K_DOWN] or keys[K_s]:
        if floor_cordy <= -2420 and player_cordy <= 1050 and player_cordy >= height // 2:
            player_cordy += speed
        elif floor_cordy >= -2420 and player_cordy == height // 2:
            floor_cordy -= speed
        elif player_cordy <= height // 2:
            player_cordy += speed

        char = pygame.transform.rotate(char, abs(360 - rotation + 180))
        rotation = 180

    elif keys[K_UP] or keys[K_w]:
        if floor_cordy >= 3500 and player_cordy >= 30 and player_cordy <= height // 2:
            player_cordy -= speed
        elif floor_cordy <= 3500 and player_cordy == height // 2:
            floor_cordy += speed
        elif player_cordy >= height // 2:
            player_cordy -= speed

        char = pygame.transform.rotate(char, abs(360 - rotation))
        rotation = 0
      
    elif keys[K_LEFT] or keys[K_a]:
        if floor_cordx >= 4500 and player_cordx >= 30 and player_cordx <= width // 2:
            player_cordx -= speed
        elif floor_cordx <= 4500 and player_cordx == width // 2:
            floor_cordx += speed
        elif player_cordx >= width // 2:
            player_cordx -= speed

        char = pygame.transform.rotate(char, abs(360 - rotation + 90))
        rotation = 90
            
    elif keys[K_RIGHT] or keys[K_d]:
        if floor_cordx <= -2580 and player_cordx <= 1890 and player_cordx >= width // 2:
            player_cordx += speed
        elif floor_cordx >= -2580 and player_cordx == width // 2:
            floor_cordx -= speed
        elif player_cordx <= width // 2:
            player_cordx += speed

        char = pygame.transform.rotate(char, abs(360 - rotation + 270))
        rotation = 270

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
        count = 0

    floor_rect.center = floor_cordx, floor_cordy
    player_rect.center = player_cordx, player_cordy
    screen.blit(floor, floor_rect)
    screen.blit(char, player_rect)
    pygame.display.update()

pygame.quit()

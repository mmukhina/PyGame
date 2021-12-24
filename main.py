import pygame
from pygame.locals import *

RED = (255, 0, 0)
GRAY = (150, 150, 150)

pygame.init()
w, h = 900, 700
screen = pygame.display.set_mode((w, h))
running = True

floor = pygame.image.load('pictures/map.png')
char = pygame.image.load("pictures/char.png")
player_cordx = 900 // 2 
player_cordy = 700 // 2
floor_cordx = 900 // 2
floor_cordy = 700 // 2

floor_rect = floor.get_rect()
floor_rect.center = floor_cordx, floor_cordy

player_rect = char.get_rect()
player_rect.center = player_cordx, player_cordy
rotation = 0

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[K_DOWN] or keys[K_s]:
        if floor_cordy <= -2800 and player_cordy <= 670 and player_cordy >= 350:
            player_cordy += 1
        elif floor_cordy >= -2800 and player_cordy == 350:
            floor_cordy -= 1
        elif player_cordy <= 350:
            player_cordy += 1

        char = pygame.transform.rotate(char, abs(360 - rotation + 180))
        rotation = 180

    elif keys[K_UP] or keys[K_w]:
        if floor_cordy >= 3500 and player_cordy >= 30 and player_cordy <= 350:
            player_cordy -= 1
        elif floor_cordy <= 3500 and player_cordy == 350:
            floor_cordy += 1
        elif player_cordy >= 350:
            player_cordy -= 1

        char = pygame.transform.rotate(char, abs(360 - rotation))
        rotation = 0
      
    elif keys[K_LEFT] or keys[K_a]:
        if floor_cordx >= 4500 and player_cordx >= 30 and player_cordx <= 450:
            player_cordx -= 1
        elif floor_cordx <= 4500 and player_cordx == 450:
            floor_cordx += 1
        elif player_cordx >= 450:
            player_cordx -= 1

        char = pygame.transform.rotate(char, abs(360 - rotation + 90))
        rotation = 90
            
    elif keys[K_RIGHT] or keys[K_d]:
        if floor_cordx <= -3600 and player_cordx <= 870 and player_cordx >= 450:
            player_cordx += 1
        elif floor_cordx >= -3600 and player_cordx == 450:
            floor_cordx -= 1
        elif player_cordx <= 450:
            player_cordx += 1

        char = pygame.transform.rotate(char, abs(360 - rotation + 270))
        rotation = 270



    floor_rect.center = floor_cordx, floor_cordy
    player_rect.center = player_cordx, player_cordy

    screen.blit(floor, floor_rect)
    screen.blit(char, player_rect)
    pygame.display.update()

pygame.quit()

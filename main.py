# Импортируем необходимые библиотеки
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


# Класс динозавров
class Dino(pygame.sprite.Sprite):
    def __init__(self, down, left, right, up, die, down_kill, up_kill,
                 left_kill, right_kill, road, maps, *group):
        super().__init__(*group)
        # Списки для анимации
        self.dino_down, self.dino_left, self.dino_right = down, left, right
        self.dino_up, self.dino_die, self.dino_down_kill = up, die, down_kill
        self.dino_up_kill, self.dino_left_kill = up_kill, left_kill
        self.dino_right_kill = right_kill

        # Константы
        self.index = 0
        self.get_killed = 0
        self.attack = 0
        self.wall = 0
        self.direction = "dowm"
        self.image = self.dino_down[self.index]

        # Присваиваем случайное место на карте
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(-2500, 2500)
        self.rect.y = random.randint(-2000, 2000)

        # Проверяем попал ли динозавр на дом
        while pygame.sprite.collide_mask(self, maps):
            self.rect.x = random.randint(-2500, 2500)
            self.rect.y = random.randint(-2000, 2000)

    def update(self, move, x, y, health, speed, bullet, player, maps, road):
        if health > 0:
            # Перемещение в зависимости от игрока
            if move == "down":
                self.rect = self.rect.move(0, - speed)
            elif move == "up":
                self.rect = self.rect.move(0, speed)
            elif move == "left":
                self.rect = self.rect.move(speed, 0)
            elif move == "right":
                self.rect = self.rect.move(- speed, 0)

            elif move == "down rev":
                self.rect = self.rect.move(0, speed)
            elif move == "up rev":
                self.rect = self.rect.move(0, - speed)
            elif move == "left rev":
                self.rect = self.rect.move(- speed, 0)
            elif move == "right rev":
                self.rect = self.rect.move(speed, 0)

            if self.get_killed == 0:
                # Если соприкасается с игроком - атаковать
                if pygame.sprite.spritecollide(self, player, False):
                    if self.direction == "left":
                        if self.index >= len(self.dino_left_kill) * 5:
                            self.index = 0
                        self.image = self.dino_left_kill[self.index // 5]
                    elif self.direction == "right":
                        if self.index >= len(self.dino_right_kill) * 5:
                            self.index = 0
                        self.image = self.dino_right_kill[self.index // 5]
                    elif self.direction == "up":
                        if self.index >= len(self.dino_up_kill) * 5:
                            self.index = 0
                        self.image = self.dino_up_kill[self.index // 5]
                    elif self.direction == "down":
                        if self.index >= len(self.dino_down_kill) * 5:
                            self.index = 0
                        self.image = self.dino_down_kill[self.index // 5]

                # Если нет вычислить положение относительно игрока
                else:
                    if self.rect.x > x + 30:
                        self.left(maps)

                        if self.wall == 1:
                            if self.rect.y > y + 30:
                                self.up(maps)
                            else:
                                self.down(maps)

                    elif self.rect.x < x - 30:
                        self.right(maps)

                        if self.wall == 1:
                            if self.rect.y > y + 30:
                                self.up(maps)
                            else:
                                self.down(maps)

                    elif self.rect.y > y + 30:
                        self.up(maps)

                        if self.wall == 1:
                            if self.rect.x < x - 30:
                                self.right(maps)
                            else:
                                self.left(maps)

                    elif self.rect.y < y - 30:
                        self.down(maps)

                        if self.wall == 1:
                            if self.rect.x < x - 30:
                                self.right(maps)
                            else:
                                self.left(maps)

                    self.wall = 0
                    self.attack = 0

                self.index += 1

                # Если пуля соприкасается с динозавром - он умирает
                if pygame.sprite.spritecollide(self, bullet, True):
                    self.get_killed = 1

            else:
                # Анимация после попадания пули
                if self.get_killed >= len(self.dino_die) * 5 + 5:
                    self.kill()

                elif self.get_killed < len(self.dino_die) * 5:
                    self.image = self.dino_die[self.get_killed // 5]

                self.get_killed += 1

        else:
            self.image = self.dino_down[0]

    def left(self, maps):
        self.rect = self.rect.move(-7, 0)

        # Столкновение со стеной
        if pygame.sprite.collide_mask(self, maps) and self.wall == 0:
            self.rect = self.rect.move(7, 0)
            self.wall = 1

        else:
            if self.index >= len(self.dino_left) * 5:
                self.index = 0
            self.image = self.dino_left[self.index // 5]
            self.direction = "left"
            self.wall = 0

    def right(self, maps):
        self.rect = self.rect.move(7, 0)

        # Столкновение со стеной
        if pygame.sprite.collide_mask(self, maps) and self.wall == 0:
            self.rect = self.rect.move(-7, 0)
            self.wall = 1

        else:
            if self.index >= len(self.dino_right) * 5:
                self.index = 0
            self.image = self.dino_right[self.index // 5]
            self.direction = "right"
            self.wall = 0

    def up(self, maps):
        self.rect = self.rect.move(0, -7)

        # Столкновение со стеной
        if pygame.sprite.collide_mask(self, maps) and self.wall == 0:
            self.rect = self.rect.move(0, 7)
            self.wall = 1

        else:
            if self.index >= len(self.dino_up) * 5:
                self.index = 0
            self.image = self.dino_up[self.index // 5]
            self.direction = "up"
            self.wall = 0

    def down(self, maps):
        self.rect = self.rect.move(0, 7)

        # Столкновение со стеной
        if pygame.sprite.collide_mask(self, maps)and self.wall == 0:
            self.rect = self.rect.move(0, -7)
            self.wall = 1

        else:
            if self.index >= len(self.dino_down) * 5:
                self.index = 0
            self.image = self.dino_down[self.index // 5]
            self.direction = "down"
            self.wall = 0


# Класс летящих пуль
class Shooting_bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, *group):
        super().__init__(*group)
        # Рисуем шарик - пуля
        radius = 4
        self.image = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA, 32)

        pygame.draw.circle(self.image, pygame.Color("grey"),
                           (radius, radius), radius)

        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)

        # Начальная позиция и движение
        self.rect.x = x
        self.rect.y = y
        self.direction = direction
        self.count = 0

    def update(self, move, speed):
        # Передвигаем пулю вперед
        if self.direction in ["down", "down stop"]:
            self.rect = self.rect.move(0, 20)
        elif self.direction in ["up", "up stop"]:
            self.rect = self.rect.move(0, -20)
        elif self.direction in ["left", "left stop"]:
            self.rect = self.rect.move(-20, 0)
        elif self.direction in ["right", "right stop"]:
            self.rect = self.rect.move(20, 0)

        # Перемещение в зависимости от игрока
        if move == "down":
            self.rect = self.rect.move(0, - speed)
        elif move == "up":
            self.rect = self.rect.move(0, speed)
        elif move == "left":
            self.rect = self.rect.move(speed, 0)
        elif move == "right":
            self.rect = self.rect.move(- speed, 0)

        self.count += 1

        # Пуля исчезает
        if self.count == 20:
            self.kill()


# Класс сундуков с пулями
class Bullet(pygame.sprite.Sprite):
    def __init__(self, maps, road, *group):
        super().__init__(*group)
        # Загружаем картинки
        self.fir_image = pygame.image.load("pictures/bullets_pile.png")
        self.sec_image = pygame.image.load("pictures/bullets_pile_b.png")
        self.image = self.sec_image
        # Присваиваем случайное место на карте
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(-2500, 2500)
        self.rect.y = random.randint(-2000, 2000)

        # Проверяем попал ли на дом
        while (pygame.sprite.collide_mask(self, maps) or
               not pygame.sprite.spritecollide(self, road, False)):
            self.rect.x = random.randint(-2500, 2500)
            self.rect.y = random.randint(-2000, 2000)

    def update(self, direction, pick, speed, player, road, maps):
        # Проверяем попал ли на дом
        while (pygame.sprite.collide_mask(self, maps) or
               not pygame.sprite.spritecollide(self, road, False)):
            self.rect.x = random.randint(-2500, 2500)
            self.rect.y = random.randint(-2000, 2000)

        self.image = self.fir_image

        # Если соприкасается с игроком и зажато е меняем местоположение
        if (pygame.sprite.spritecollideany(self, player) and pick == 1):
            self.image = self.sec_image
            self.rect.x = random.randint(-2500, 2500)
            self.rect.y = random.randint(-2000, 2000)

        # Перемещение в зависимости от игрока
        if direction == "down":
            self.rect = self.rect.move(0, - speed)
        elif direction == "up":
            self.rect = self.rect.move(0, speed)
        elif direction == "left":
            self.rect = self.rect.move(speed, 0)
        elif direction == "right":
            self.rect = self.rect.move(- speed, 0)


# Класс домов
class Map(pygame.sprite.Sprite):
    def __init__(self, width, height, *group):
        super().__init__(*group)
        # Загружаем фотографию
        self.image = pygame.image.load("pictures/mask.png")

        # Располагаем по центру
        self.rect = self.image.get_rect()
        self.rect.x = (width // 2) - (self.image.get_width() // 2)
        self.rect.y = (height // 2) - (self.image.get_height() // 2)

        # Создаем маску
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, direction, health, speed):
        # Перемещение в зависимости от игрока
        if health > 0:
            if direction == "down":
                self.rect = self.rect.move(0, - speed)
            elif direction == "up":
                self.rect = self.rect.move(0, speed)
            elif direction == "left":
                self.rect = self.rect.move(speed, 0)
            elif direction == "right":
                self.rect = self.rect.move(- speed, 0)

            elif direction == "down rev":
                self.rect = self.rect.move(0, speed)
            elif direction == "up rev":
                self.rect = self.rect.move(0, - speed)
            elif direction == "left rev":
                self.rect = self.rect.move(- speed, 0)
            elif direction == "right rev":
                self.rect = self.rect.move(speed, 0)


# Класс дороги
class Road(pygame.sprite.Sprite):
    def __init__(self, img, width, height, *group):
        super().__init__(*group)
        # Загружаем фотографию
        self.image = img

        # Располагаем по центру
        self.rect = self.image.get_rect()
        self.rect.x = (width // 2) - (self.image.get_width() // 2)
        self.rect.y = (height // 2) - (self.image.get_height() // 2)

    def update(self, direction, health, speed):
        # Перемещение в зависимости от игрока
        if health > 0:
            if direction == "down":
                self.rect = self.rect.move(0, - speed)
            elif direction == "up":
                self.rect = self.rect.move(0, speed)
            elif direction == "left":
                self.rect = self.rect.move(speed, 0)
            elif direction == "right":
                self.rect = self.rect.move(- speed, 0)

            elif direction == "down rev":
                self.rect = self.rect.move(0, speed)
            elif direction == "up rev":
                self.rect = self.rect.move(0, - speed)
            elif direction == "left rev":
                self.rect = self.rect.move(- speed, 0)
            elif direction == "right rev":
                self.rect = self.rect.move(speed, 0)


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, width, height, down, left, right, up, ghost, *group):
        super().__init__(*group)
        # Загружаем списки анимаций
        self.player_down = down
        self.player_up = up
        self.player_left = left
        self.player_right = right
        self.ghost = ghost

        self.index = 0
        self.count = 0
        self.image = self.player_down[self.index]

        # Располагаем по центру
        self.rect = self.image.get_rect()
        self.rect.x = (width // 2) - 30
        self.rect.y = (height // 2) - 30

    def update(self, health, direction, speed):
        if health > 0:
            # В зависимости от скорости игрока меняем скорость кадров
            if speed == 6:
                speed = 5
            else:
                speed = 2

            # Анимации движенния игрока
            if direction == "down":
                if self.index >= len(self.player_down) * speed:
                    self.index = 0
                self.image = self.player_down[self.index // speed]

            elif direction == "up":
                if self.index >= len(self.player_up) * speed:
                    self.index = 0
                self.image = self.player_up[self.index // speed]

            elif direction == "left":
                if self.index >= len(self.player_left) * speed:
                    self.index = 0
                self.image = self.player_left[self.index // speed]

            elif direction == "right":
                if self.index >= len(self.player_right) * speed:
                    self.index = 0
                self.image = self.player_right[self.index // speed]

            elif direction == "down stop":
                self.image = self.player_down[0]

            elif direction == "left stop":
                self.image = self.player_left[0]

            elif direction == "right stop":
                self.image = self.player_right[0]

            elif direction == "up stop":
                self.image = self.player_up[0]

            self.index += 1
        else:
            # Анимация приведения
            if self.count >= len(self.ghost) * 20:
                self.count = 0
            self.image = self.ghost[self.count // 20]
            self.count += 1
            self.rect = self.rect.move(0, -3)


# Класс барьер для игрока - конец поля
class Mask(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2, borders):
        super().__init__(borders)
        # Добавляем прямую в группу
        self.add(borders)
        if x1 == x2:
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)

    def update(self, direction, health, speed):
        # Перемещение в зависимости от игрока
        if health > 0:
            if direction == "down":
                self.rect = self.rect.move(0, - speed)
            elif direction == "up":
                self.rect = self.rect.move(0, speed)
            elif direction == "left":
                self.rect = self.rect.move(speed, 0)
            elif direction == "right":
                self.rect = self.rect.move(- speed, 0)

            elif direction == "down rev":
                self.rect = self.rect.move(0, speed)
            elif direction == "up rev":
                self.rect = self.rect.move(0, - speed)
            elif direction == "left rev":
                self.rect = self.rect.move(- speed, 0)
            elif direction == "right rev":
                self.rect = self.rect.move(speed, 0)


# Класс игры
class Game():
    def __init__(self):
        self.stage = 1
        self.sound_state = 1
        self.counter = 0

        while True:
            if self.stage == 1:
                # Стартовое окно
                self.start()

            elif self.stage == 2:
                # Основная игра
                if self.counter == 0:
                    # Загружаем данные один раз за работу программы
                    pygame.display.set_caption('Last Monday')
                    pygame.init()
                    self.screen = pygame.display.set_mode((self.width,
                                                           self.height))
                    pygame.mixer.pre_init(44100, -16, 1, 512)

                    b1 = -1570
                    b2 = 2930
                    b3 = -730
                    b4 = 2260
                    # Создаем барьер для игрока
                    Mask(b1, b3, b2, b4, self.mask_group)
                    Mask(b2, b3, b2, b4, self.mask_group)
                    Mask(b1, b3, b1, b4, self.mask_group)
                    Mask(b1, b4, b2, b4, self.mask_group)

                    # Создаем карту города
                    self.maps = Map(self.width, self.height, self.map_group)
                    Road(self.road, self.width, self.height, self.map_group)

                    # Создаем игрока
                    self.player = Player(self.width, self.height,
                                         self.player_down, self.player_left,
                                         self.player_right, self.player_up,
                                         self.player_ghost, self.player_group)

                    # Создаем 10 коробок с пулями
                    for i in range(10):
                        Bullet(self.maps, self.map_group, self.bullets_group)

                    # Создаем 3 динозавра
                    while len(self.dino_group.sprites()) != 3:
                        Dino(self.dino_down, self.dino_left, self.dino_right,
                             self.dino_up, self.dino_die,
                             self.dino_down_kill, self.dino_up_kill,
                             self.dino_left_kill, self.dino_right_kill,
                             self.mask_group, self.maps, self.dino_group)

                    pygame.display.update()

                    self.counter = 1

                self.main()

            elif self.stage == 3:
                # Окно паузы
                self.pause()

    def main(self):
        # Создаем экран
        pygame.display.set_caption('Last Monday')
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.mixer.pre_init(44100, -16, 1, 512)
        self.clock = pygame.time.Clock()
        self.growl_count = 0

        # Основной игровой цикл
        while self.main_game_running:
            if self.health != 0:
                self.past_shot += 1
                # Если джойстик не подключен
                if self.joystick != 1:
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            self.running = False
                            break

                        if event.type == pygame.KEYDOWN:
                            # Кнопка ESC
                            if event.key == pygame.K_ESCAPE:
                                pygame.quit()
                                self.stage = 3
                                return

                            # Кнопка E
                            if event.key == pygame.K_e:
                                self.pick = 1

                            # Кнопка Левый шифт
                            if event.key == pygame.K_LSHIFT:
                                self.speed = 15
                            # Ограничение на частоту стрельбы
                            if self.past_shot > 35 and self.no_bullet > 0:
                                if event.key == pygame.K_SPACE:
                                    self.no_bullet -= 1
                                    # Создаем пулю
                                    Shooting_bullet((self.width // 2),
                                                    (self.height // 2),
                                                    self.direction,
                                                    self.shooting_bullet_group)
                                    # Звук пули
                                    if self.sound_state == 1:
                                        self.shot_sound.play()
                                    self.past_shot = 0

                            # Движение игрока по клавишам
                            if (event.key == pygame.K_DOWN) or (
                                    event.key == pygame.K_s):
                                self.direction = "down"
                            elif event.key == pygame.K_UP or (
                                    event.key == pygame.K_w):
                                self.direction = "up"
                            elif event.key == pygame.K_LEFT or (
                                    event.key == pygame.K_a):
                                self.direction = "left"
                            elif event.key == pygame.K_RIGHT or (
                                    event.key == pygame.K_d):
                                self.direction = "right"

                        # Если клавишу отпустили - остоновить игрока
                        if event.type == pygame.KEYUP:
                            if (event.key == pygame.K_DOWN or
                                    event.key == pygame.K_s) and (
                                        self.direction == "down"):
                                self.direction = "down stop"
                            elif (event.key == pygame.K_UP or
                                    event.key == pygame.K_w) and (
                                        self.direction == "up"):
                                self.direction = "up stop"
                            elif (event.key == pygame.K_LEFT or
                                    event.key == pygame.K_a) and (
                                        self.direction == "left"):
                                self.direction = "left stop"
                            elif (event.key == pygame.K_RIGHT or
                                    event.key == pygame.K_d) and (
                                    self.direction == "right"):
                                self.direction = "right stop"

                            if event.key == pygame.K_e:
                                self.pick = 0

                            if event.key == pygame.K_LSHIFT:
                                self.speed = 6

                    self.update()

                else:
                    # Получаем данные с джойстика
                    self.joystick_movement()

                    # Проверяем если была зажата кнопка выхода
                    if self.joy_move in [b'1D\n', b'1U\n', b'1L\n', b'1R\n',
                                         b'1N\n']:
                        pygame.quit()
                        self.stage = 3
                        break

                    # Проверяем если джостик перемещался
                    if self.joy_move in [b'1D\n', b'2D\n', b'3D\n', b'4D\n',
                                         b'5D\n']:
                        self.direction = "down"
                    elif self.joy_move in [b'1L\n', b'2L\n', b'3L\n', b'4L\n',
                                           b'5L\n']:
                        self.direction = "left"
                    elif self.joy_move in [b'1R\n', b'2R\n', b'3R\n', b'4R\n',
                                           b'5R\n']:
                        self.direction = "right"
                    elif self.joy_move in [b'1U\n', b'2U\n', b'3U\n', b'4U\n',
                                           b'5U\n']:
                        self.direction = "up"

                    if self.joy_move in [b'1N\n', b'2N\n', b'3N\n', b'4N\n',
                                         b'5N\n']:
                        if self.direction == "down":
                            self.direction = "down stop"
                        elif self.direction == "up":
                            self.direction = "up stop"
                        elif self.direction == "left":
                            self.direction = "left stop"
                        elif self.direction == "right":
                            self.direction = "right stop"

                    # Проверяем если была зажата кнопка взять
                    if self.joy_move in [b'2D\n', b'2U\n', b'2L\n', b'2R\n',
                                         b'2N\n']:
                        self.pick = 1
                    else:
                        self.pick = 0

                    # Проверяем если была зажата кнопка бежать
                    if self.joy_move in [b'3D\n', b'3U\n', b'3L\n', b'3R\n',
                                         b'3N\n']:
                        self.speed = 15
                    else:
                        self.speed = 6

                    # Проверяем если была зажата кнопка стрелять
                    if self.joy_move in [b'4D\n', b'4U\n', b'4L\n', b'4R\n',
                                         b'4N\n'] and self.no_bullet > 0 and (
                                             self.past_shot > 50):
                        self.no_bullet -= 1
                        # Создаем пулю
                        Shooting_bullet((self.width // 2), (self.height // 2),
                                        self.direction,
                                        self.shooting_bullet_group)
                        # Звук пули
                        if self.sound_state == 1:
                            self.shot_sound.play()
                        self.past_shot = 0

                    self.update()

            else:
                pygame.quit()
                self.stage = 3
                return

    def joystick_movement(self):
        try:
            # Попытка получить данные с джойстика
            data = self.arduino.readline()
        except Exception:
            # При ошибке приостанавливаем игру
            data = b'1N\n'
            self.arduino.close()

        if data != b'':
            self.joy_move = data

    def update(self):
        # Проверяем выносливость и меняем скорость
        if self.speed == 15 and self.stamina > 0:
            self.stamina -= 1
        elif self.speed == 6 and self.stamina != 255:
            self.stamina += 0.5
        if self.speed == 15 and self.stamina < 20:
            self.speed = 6

        # Обновляем отслеживание
        self.text_update()

        # Проверка на соприкосновение с коробкой с пулями
        pick_up = pygame.sprite.groupcollide(self.player_group,
                                             self.bullets_group, False, False)

        # Добавляем пули
        if pick_up != {} and self.pick == 1:
            self.no_bullet += (len(pick_up[list(pick_up.keys())[0]]) * 5)

        # Отрисовка пуль
        self.bullets_group.draw(self.screen)
        self.bullets_group.update(self.direction, self.pick, self.speed,
                                  self.player_group, self.map_group, self.maps)
        self.shooting_bullet_group.draw(self.screen)
        self.shooting_bullet_group.update(self.direction, self.speed)

        # Проверяем попала ли пуля в динозавра
        shot = pygame.sprite.groupcollide(self.shooting_bullet_group,
                                          self.dino_group, False, False)
        if shot != {}:
            self.no_killed += (len(shot[list(shot.keys())[0]]))
            self.dino_count -= 1
            if self.dino_count <= 48:
                self.dino_count += 2
                # Создаем новых динозавров
                while len(self.dino_group.sprites()) != self.dino_count:
                    Dino(self.dino_down, self.dino_left, self.dino_right,
                         self.dino_up, self.dino_die, self.dino_down_kill,
                         self.dino_up_kill, self.dino_left_kill,
                         self.dino_right_kill, self.mask_group, self.maps,
                         self.dino_group,)

                    self.dino_group.update(self.direction,
                                           self.width // 2 - 60,
                                           self.height // 2 - 60, self.health,
                                           self.speed,
                                           self.shooting_bullet_group,
                                           self.player_group, self.maps,
                                           self.mask_group)

        # Проверяем на соприкосновение игрока и динозавтра
        life = pygame.sprite.groupcollide(
            self.player_group, self.dino_group, False, False)

        # Звук когтей
        if life != {}:
            self.hit_count += 1
            if self.sound_state == 1 and self.claw_count > 100:
                self.claws_sound.play()
                self.claw_count = 0
        else:
            self.claws_sound.stop()

        self.claw_count += 1

        # Уменьшаем здоровье при атаке
        if self.hit_count == 100:
            self.health -= 1
            self.hit_count = 0

        # Звук динозавров
        if self.growl_count > self.growl_random and self.sound_state == 1:
            # Выбираем рандомный из списка
            temp = random.randint(0, 2)
            self.growl_sound[temp].play()
            self.growl_random = random.randint(150, 400)
            self.growl_count = 0

        self.growl_count += 1

        # Звук шагов игрока
        if self.sound_state == 1 and self.direction in [
                "down", "left", "right", "up"] and self.footsteps_count == 0:
            self.footsteps_sound.play(-1)
            self.footsteps_count = 1
        elif self.direction not in ["down", "left", "right", "up"]:
            self.footsteps_count = 0
            self.footsteps_sound.stop()

        # Рисуем динозавров
        self.dino_group.draw(self.screen)
        self.dino_group.update(self.direction, self.width // 2 - 60,
                               self.height // 2 - 60, self.health, self.speed,
                               self.shooting_bullet_group, self.player_group,
                               self.maps, self.mask_group)

        if self.health > 0:
            # Рисуем игрока
            self.player_group.draw(self.screen)
            self.player_group.update(self.health, self.direction, self.speed)
            pygame.display.update()
        else:
            # Остановка игры при отсутствие жизни
            self.claws_sound.stop()
            self.footsteps_sound.stop()
            for i in range(80):
                self.text_update()
                self.dino_group.draw(self.screen)
                self.dino_group.update(self.direction, self.width // 2 - 60,
                                       self.height // 2 - 60, self.health,
                                       self.speed, self.shooting_bullet_group,
                                       self.player_group, self.maps,
                                       self.mask_group)

                self.player_group.draw(self.screen)
                self.player_group.update(
                    self.health, self.direction, self.speed)
                pygame.display.update()

        self.clock.tick(100)

    def text_update(self):
        # Отрисовываем карту города
        self.mask_group.draw(self.screen)
        self.mask_group.update(self.direction, self.health, self.speed)
        self.road_group.draw(self.screen)
        self.road_group.update(self.direction, self.health, self.speed)
        self.map_group.draw(self.screen)
        self.map_group.update(self.direction, self.health, self.speed)

        # Проверяем столкновение игрока с домом
        if pygame.sprite.collide_mask(
            self.player, self.maps) or pygame.sprite.groupcollide(
                self.player_group, self.mask_group, False, False):
            if self.direction == "down":
                self.direction = "down stop"
                self.map_group.update("down rev", self.health, self.speed)
                self.mask_group.update("down rev", self.health, self.speed)
            elif self.direction == "up":
                self.direction = "up stop"
                self.map_group.update("up rev", self.health, self.speed)
                self.mask_group.update("up rev", self.health, self.speed)
            elif self.direction == "left":
                self.direction = "left stop"
                self.map_group.update("left rev", self.health, self.speed)
                self.mask_group.update("left rev", self.health, self.speed)
            elif self.direction == "right":
                self.direction = "right stop"
                self.map_group.update("right rev", self.health, self.speed)
                self.mask_group.update("right rev", self.health, self.speed)

        # Рисуем полосу для отслеживания
        s = pygame.Surface((self.width, 50))
        s.set_alpha(128)
        s.fill((255, 255, 255))
        self.screen.blit(s, (0, 0))

        font1 = pygame.font.SysFont('comicsansms', 19)

        # Данные для отслеживания
        # Выносливость
        pygame.draw.rect(self.screen, (205, 24, 24), pygame.Rect(
            780, 10, self.stamina, 30), border_radius=3)

        text = font1.render("Stamina", True, (0, 0, 0))
        self.screen.blit(text, (670, 10))

        # Жизни
        for i in range(self.health):
            self.screen.blit(self.heart, [10 + i * 40, 10])

        # Количество пуль
        self.screen.blit(self.bullet, [300, 10])

        temp = "X " + str(self.no_bullet)
        text = font1.render(temp, True, (0, 0, 0))
        self.screen.blit(text, (350, 11))

        # Количество убитых монстров
        self.screen.blit(self.monster, [500, 10])
        text = font1.render(str(self.no_killed), True, (0, 0, 0))
        self.screen.blit(text, (550, 11))

    def load(self):
        # Размер экрана пользователя
        self.width, self.height = pyautogui.size()

        # Загружаем фотографии
        self.road = pygame.image.load('pictures/map.jpg')
        self.heart = pygame.image.load("pictures/heart.png")
        self.bullet = pygame.image.load("pictures/bullet.png")
        self.monster = pygame.image.load("pictures/monster.png")

        # Константы
        self.joy_move = b''
        self.direction = "down_stop"
        self.health = 5
        self.no_bullet = 100
        self.no_killed = 0
        self.pick = 0
        self.shoot = 0
        self.hit_count = 0
        self.dino_count = 3
        self.counter = 0
        self.speed = 6
        self.stamina = 255
        self.past_shot = 50
        self.claw_count = 0
        self.growl_random = random.randint(150, 400)
        self.growl_count = 0
        self.footsteps_count = 0

        # Sprite группы
        self.player_group = pygame.sprite.Group()
        self.bullets_group = pygame.sprite.Group()
        self.dino_group = pygame.sprite.Group()
        self.shooting_bullet_group = pygame.sprite.Group()
        self.border_group = pygame.sprite.Group()
        self.map_group = pygame.sprite.Group()
        self.road_group = pygame.sprite.Group()
        self.mask_group = pygame.sprite.Group()

        self.main_game_running = 1

        # Загружаем списки анимаций из базы данных
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "player_down" """).fetchall()
        self.player_down = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "player_up" """).fetchall()
        self.player_up = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "player_left" """).fetchall()
        self.player_left = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "player_right" """).fetchall()
        self.player_right = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "dino_left" """).fetchall()
        self.dino_left = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "dino_right" """).fetchall()
        self.dino_right = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "dino_up" """).fetchall()
        self.dino_up = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "dino_down" """).fetchall()
        self.dino_down = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "dino_die" """).fetchall()
        self.dino_die = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "ghost" """).fetchall()
        self.player_ghost = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "dino_down_kill"
            """).fetchall()
        self.dino_down_kill = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "dino_up_kill" """).fetchall()
        self.dino_up_kill = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "dino_right_kill"
            """).fetchall()
        self.dino_right_kill = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is"dino_left_kill" """).fetchall()
        self.dino_left_kill = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "growl" """).fetchall()
        self.growl_sound = [
            pygame.mixer.Sound(i) for i in result[0][1:] if i != "no"]

        con.close()

        # Загружаем звуки
        self.footsteps_sound = pygame.mixer.Sound("Sound/footsteps.mp3")
        self.shot_sound = pygame.mixer.Sound("Sound/shot2.mp3")
        self.claws_sound = pygame.mixer.Sound("Sound/claws.wav")

    def pause(self):
        # Создаем экран паузы игры
        pygame.init()
        pygame.display.set_caption('Last Monday')
        pygame.display.set_icon(pygame.image.load("pictures/icon.ico"))
        self.screen_start = pygame.display.set_mode((self.w, self.h))

        # Загружаем анимацию экрана
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "pause_window" """).fetchall()
        self.pause_window = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "best_score" """).fetchall()
        self.best_score = int(result[0][1])

        con.close()

        # Загружаем музыку для заднего фона
        mixer.music.load("Sound/background1.mp3")
        mixer.music.play(-1)

        self.end_game = pygame.image.load("pictures/game_over.jpg")

        count = 0

        color_dark = (0, 0, 0)

        font1 = pygame.font.SysFont('comicsansms', 23)

        # Тексты для кнопок
        text = font1.render('Продолжить игру', True, (255, 255, 255))
        text2 = font1.render('Подключить джойстик', True, (255, 255, 255))
        text3 = font1.render('Подключить джойстик', True, (26, 199, 73))
        text4 = font1.render('Подключить джойстик', True, (237, 0, 0))
        text5 = font1.render('Меню', True, (255, 255, 255))
        text6 = font1.render(
            'Счет: ' + str(self.no_killed), True, (255, 255, 255))
        text7 = font1.render(
            'Нажмите, чтобы продолжить', True, (255, 255, 255))
        text8 = font1.render(
            "Лучший: " + str(self.best_score), True, (255, 255, 255))

        pygame.display.update()

        # Фиксируем позицию игрока
        if self.direction == "up":
            self.direction = "up stop"
        elif self.direction == "down":
            self.direction = "down stop"
        elif self.direction == "left":
            self.direction = "left stop"
        elif self.direction == "right":
            self.direction = "right stop"

        while self.start_running:
            # Если здоровья нет показать заставку конец игры
            if self.health == 0:
                # Проверяем если счет больше лучшего и обновляем
                if self.no_killed > self.best_score:
                    con = sqlite3.connect("database.db")
                    cur = con.cursor()
                    update = ("""Update Lists set '1' = ?
                        WHERE key = 'best_score' """)
                    cur.execute(update, (str(self.no_killed),))
                    con.commit()
                    con.close()

                    text8 = font1.render(
                        "Лучший: " + str(self.no_killed), True,
                        (255, 255, 255))

                self.screen_start.blit(self.end_game, [0, 0])

                self.screen_start.blit(text6, (self.w * 0.57 + 115,
                                               self.h * 0.82 - 20))
                self.screen_start.blit(text7, (self.w * 0.1, self.h * 0.6))

                self.screen_start.blit(text8, (self.w * 0.57 + 115,
                                               self.h * 0.82 + 25))

                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.stop = 1
                        self.start_running = False
                        pygame.quit()
                        sys.exit()

                    # При нажатии кнопки возвращаемся на главную страницу
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.stage = 1
                        pygame.quit()
                        return

                pygame.display.update()

            else:
                # Анимация заставки
                if count % 1000 == 0:
                    self.screen_start.blit(
                        self.pause_window[random.randint(0, 4)], [0, 0])

                count += 1

                # Проверяем кнопку звука
                if self.sound_state == 2:
                    self.screen_start.blit(self.sound_image1, (10, 10))
                    mixer.music.play(-1)
                    self.sound_state = 1
                elif self.sound_state == 0:
                    self.screen_start.blit(self.sound_image2, (10, 10))
                    mixer.music.stop()
                else:
                    self.screen_start.blit(self.sound_image1, (10, 10))

                # Получаем позицию мышки
                mouse = pygame.mouse.get_pos()

                # Кнопка 1
                if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and (
                        self.h * 0.62 <= mouse[1] <= self.h * 0.62 + 50):
                    pygame.draw.rect(self.screen_start, color_dark,
                                     [self.w * 0.57, self.h * 0.62, 300, 50],
                                     border_radius=10)
                    pygame.draw.rect(self.screen_start, (255, 255, 255),
                                     [self.w * 0.57, self.h * 0.62, 300, 50],
                                     1, border_radius=10)

                else:
                    pygame.draw.rect(self.screen_start, color_dark,
                                     [self.w * 0.57, self.h * 0.62, 300, 50],
                                     border_radius=10)
                    pygame.draw.rect(self.screen_start, (255, 255, 255),
                                     [self.w * 0.57, self.h * 0.62, 300, 50],
                                     2, border_radius=10)

                # Кнопка 2
                if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and (
                        self.h * 0.72 <= mouse[1] <= self.h * 0.7 + 50):
                    pygame.draw.rect(self.screen_start, color_dark,
                                     [self.w * 0.57, self.h * 0.72, 300, 50],
                                     border_radius=10)
                    pygame.draw.rect(self.screen_start, (255, 255, 255),
                                     [self.w * 0.57, self.h * 0.72, 300, 50],
                                     1, border_radius=10)

                else:
                    pygame.draw.rect(self.screen_start, color_dark,
                                     [self.w * 0.57, self.h * 0.72, 300, 50],
                                     border_radius=10)
                    pygame.draw.rect(self.screen_start, (255, 255, 255),
                                     [self.w * 0.57, self.h * 0.72, 300, 50],
                                     2, border_radius=10)

                self.screen_start.blit(
                    text, (self.w * 0.57 + 54, self.h * 0.72 + 5))

                # Кнопка 3
                if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and (
                        self.h * 0.82 <= mouse[1] <= self.h * 0.82 + 50):
                    pygame.draw.rect(self.screen_start, color_dark,
                                     [self.w * 0.57, self.h * 0.82, 300, 50],
                                     border_radius=10)
                    pygame.draw.rect(self.screen_start, (255, 255, 255),
                                     [self.w * 0.57, self.h * 0.82, 300, 50],
                                     1, border_radius=10)

                else:
                    pygame.draw.rect(self.screen_start, color_dark,
                                     [self.w * 0.57, self.h * 0.82, 300, 50],
                                     border_radius=10)
                    pygame.draw.rect(self.screen_start, (255, 255, 255),
                                     [self.w * 0.57, self.h * 0.82, 300, 50],
                                     2, border_radius=10)

                # Добавляем текст на кнопки
                self.screen_start.blit(
                    text5, (self.w * 0.57 + 115, self.h * 0.82 + 5))

                if self.joystick == 1:
                    self.screen_start.blit(
                        text3, (self.w * 0.57 + 21, self.h * 0.62 + 5))
                elif self.joystick == 0:
                    self.screen_start.blit(
                        text4, (self.w * 0.57 + 21, self.h * 0.62 + 5))
                else:
                    self.screen_start.blit(
                        text2, (self.w * 0.57 + 21, self.h * 0.62 + 5))

                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.stop = 1
                        self.start_running = False
                        pygame.quit()
                        sys.exit()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Нажатие на 2 кнопку
                        if self.w * 0.6 <= mouse[0] <= self.w * 0.6 + 180 and (
                                self.h * 0.72 <= mouse[1] and (
                                    mouse[1] <= self.h * 0.72 + 50)):
                            self.stage = 2
                            pygame.quit()
                            return

                        # Нажатие на 3 кнопку
                        elif self.w * 0.6 <= mouse[0] and (
                            mouse[0] <= self.w * 0.6 + 180) and (
                                self.h * 0.82 <= mouse[1] and (
                                    mouse[1] <= self.h * 0.82 + 50)):
                            self.stage = 1
                            pygame.quit()
                            return

                        # Нажатие на кнопку звука
                        elif 10 <= mouse[0] <= 50 and (
                                10 <= mouse[1] <= 50) and (
                                    self.sound_state == 1):
                            self.sound_state = 0

                        elif 10 <= mouse[0] and mouse[0] <= 50 and (
                                10 <= mouse[1] <= 50) and (
                                self.sound_state == 0):
                            self.sound_state = 2

                        # Нажатие на 1 кнопку
                        elif self.w * 0.57 <= mouse[0] and (
                            mouse[0] <= self.w * 0.57 + 300) and (
                                self.h * 0.62 <= mouse[1]) and (
                                    mouse[1] <= self.h * 0.62 + 50):
                            # Попытка подключиться к джойстику
                            if self.joystick_connect() == 1:
                                self.joystick = 1
                                time.sleep(2)
                                self.arduino.write(bytes("1", 'utf-8'))
                                self.joy_move = b''
                            else:
                                self.joystick = 0
                                pyautogui.alert("Джойстик не найден")

    def start(self):
        pygame.init()
        self.w = 900
        self.h = 700

        # Загружаем анимацию экрана из базы данных
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        result = cur.execute(
            """SELECT * FROM Lists WHERE key is "first_window" """).fetchall()
        self.first_window = [
            pygame.image.load(i) for i in result[0][1:] if i != "no"]

        con.close()

        # загружаем фотогрфии
        self.sound_image1 = pygame.image.load("pictures/sound1.png")
        self.sound_image2 = pygame.image.load("pictures/sound2.png")

        self.help_image = pygame.image.load("pictures/help.png")
        self.cross_image = pygame.image.load("pictures/cross.png")

        self.loading_image = pygame.image.load("pictures/loading.jpg")
        self.instruction_image = pygame.image.load("pictures/instruction.jpg")

        pygame.display.set_caption('Last Monday')
        pygame.display.set_icon(pygame.image.load("pictures/icon.ico"))
        self.screen_start = pygame.display.set_mode((self.w, self.h))

        # Константы
        self.start_running = 1
        self.joystick = 3
        self.speed = 1
        return_to_main = 0
        self.help_state = 0

        # Загружаем музыку для заднего фона
        mixer.music.load("Sound/background1.mp3")
        mixer.music.play(-1)

        self.count = 0

        self.color_dark = (0, 0, 0)

        font1 = pygame.font.SysFont('comicsansms', 23)

        # Текст для кнопок
        self.text = font1.render('Начать игру', True, (255, 255, 255))
        self.text2 = font1.render('Подключить джойстик', True, (255, 255, 255))
        self.text3 = font1.render('Подключить джойстик', True, (26, 199, 73))
        self.text4 = font1.render('Подключить джойстик', True, (237, 0, 0))
        self.text5 = font1.render('Закрыть игру', True, (255, 255, 255))

        pygame.display.update()

        while self.start_running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.stop = 1
                    self.start_running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()
                    # Нажатие на 2 кнопку
                    if self.w * 0.6 <= mouse[0] <= self.w * 0.6 + 180 and (
                        self.h * 0.72 <= mouse[1] <= self.h * 0.72 + 50) and (
                            self.help_state == 0):
                        self.screen_start.blit(self.loading_image, (0, 0))
                        self.stage = 2
                        pygame.display.update()
                        self.load()
                        pygame.quit()
                        return

                    # Нажатие на 3 кнопку
                    elif self.w * 0.6 <= mouse[0] <= self.w * 0.6 + 180 and (
                        self.h * 0.82 <= mouse[1] <= self.h * 0.82 + 50) and (
                            self.help_state == 0):
                        pygame.quit()
                        sys.exit()

                    # Нажатие на кнопку звука
                    elif 10 <= mouse[0] <= 50 and 10 <= mouse[1] <= 50 and (
                            self.sound_state == 1):
                        self.sound_state = 0

                    elif 10 <= mouse[0] <= 50 and 10 <= mouse[1] <= 50 and (
                            self.sound_state == 0):
                        self.sound_state = 2

                    # Нажатие на кнопку помощи
                    if 10 <= mouse[0] <= 50 and 60 <= mouse[1] <= 100 and (
                            self.help_state == 1):
                        self.help_state = 0

                    elif 10 <= mouse[0] <= 50 and 60 <= mouse[1] <= 100 and (
                            self.help_state == 0):
                        self.help_state = 1

                    # Нажатие на 1 кнопку
                    elif self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and (
                        self.h * 0.62 <= mouse[1] <= self.h * 0.62 + 50) and (
                            self.help_state == 0):
                        # Попытка подключения к джойстику
                        if self.joystick_connect() == 1:
                            self.joystick = 1
                            time.sleep(2)
                            self.arduino.write(bytes("1", 'utf-8'))
                            self.joy_move = b''
                        else:
                            self.joystick = 0
                            pyautogui.alert("Джойстик не найден")

            self.update_start()

    def update_start(self):
        # Анимация заставки
        if self.count % 1000 == 0:
            self.random = random.randint(0, 4)

        self.screen_start.blit(self.first_window[self.random], [0, 0])

        self.count += 1

        # Проверяем нажатие кнопки звука
        if self.sound_state == 2:
            self.screen_start.blit(self.sound_image1, (10, 10))
            mixer.music.play(-1)
            self.sound_state = 1
        elif self.sound_state == 0:
            self.screen_start.blit(self.sound_image2, (10, 10))
            mixer.music.stop()
        else:
            self.screen_start.blit(self.sound_image1, (10, 10))

        #  Получаем позицию мышки
        mouse = pygame.mouse.get_pos()

        # Кнопка 1
        if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and (
            self.h * 0.62 <= mouse[1] <= self.h * 0.62 + 50) and (
                self.help_state == 0):
            pygame.draw.rect(self.screen_start, self.color_dark,
                             [self.w * 0.57, self.h * 0.62, 300, 50],
                             border_radius=10)
            pygame.draw.rect(self.screen_start, (255, 255, 255),
                             [self.w * 0.57, self.h * 0.62, 300, 50], 1,
                             border_radius=10)

        else:
            pygame.draw.rect(self.screen_start, self.color_dark,
                             [self.w * 0.57, self.h * 0.62, 300, 50],
                             border_radius=10)
            pygame.draw.rect(self.screen_start, (255, 255, 255),
                             [self.w * 0.57, self.h * 0.62, 300, 50], 2,
                             border_radius=10)

        # Кнопка 2
        if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and (
            self.h * 0.72 <= mouse[1] <= self.h * 0.7 + 50) and (
                self.help_state == 0):
            pygame.draw.rect(self.screen_start, self.color_dark,
                             [self.w * 0.57, self.h * 0.72, 300, 50],
                             border_radius=10)
            pygame.draw.rect(self.screen_start, (255, 255, 255),
                             [self.w * 0.57, self.h * 0.72, 300, 50],
                             1, border_radius=10)

        else:
            pygame.draw.rect(self.screen_start, self.color_dark,
                             [self.w * 0.57, self.h * 0.72, 300, 50],
                             border_radius=10)
            pygame.draw.rect(self.screen_start, (255, 255, 255),
                             [self.w * 0.57, self.h * 0.72, 300, 50],
                             2, border_radius=10)

        self.screen_start.blit(
            self.text, (self.w * 0.57 + 85, self.h * 0.72 + 5))

        # Кнопка 3
        if self.w * 0.57 <= mouse[0] <= self.w * 0.57 + 300 and (
            self.h * 0.82 <= mouse[1] <= self.h * 0.82 + 50) and (
                self.help_state == 0):
            pygame.draw.rect(self.screen_start, self.color_dark,
                             [self.w * 0.57, self.h * 0.82, 300, 50],
                             border_radius=10)
            pygame.draw.rect(self.screen_start, (255, 255, 255),
                             [self.w * 0.57, self.h * 0.82, 300, 50],
                             1, border_radius=10)

        else:
            pygame.draw.rect(self.screen_start, self.color_dark,
                             [self.w * 0.57, self.h * 0.82, 300, 50],
                             border_radius=10)
            pygame.draw.rect(self.screen_start, (255, 255, 255),
                             [self.w * 0.57, self.h * 0.82, 300, 50],
                             2, border_radius=10)

        # добавляем текст на кнопки
        self.screen_start.blit(
            self.text5, (self.w * 0.57 + 75, self.h * 0.82 + 5))

        if self.joystick == 1:
            self.screen_start.blit(
                self.text3, (self.w * 0.57 + 21, self.h * 0.62 + 5))
        elif self.joystick == 0:
            self.screen_start.blit(
                self.text4, (self.w * 0.57 + 21, self.h * 0.62 + 5))
        else:
            self.screen_start.blit(
                self.text2, (self.w * 0.57 + 21, self.h * 0.62 + 5))

        if self.help_state == 0:
            self.screen_start.blit(self.help_image, (10, 60))
        else:
            self.screen_start.blit(self.cross_image, (10, 60))
            self.screen_start.blit(self.instruction_image, (100, 100))

        pygame.display.update()

    def findArduinoUnoPort(self):
        # Ищем открытый порт
        portList = list(serial.tools.list_ports.comports())
        for port in portList:
            if ("VID:PID=2341:0043" in port[0] or
                "VID:PID=2341:0043" in port[1] or
               "VID:PID=2341:0043" in port[2]):
                    return port[0]

    def joystick_connect(self):
        # Попытка подключиться к джойстику
        try:
            self.arduino.close()
            unoPort = True
        except Exception:
            unoPort = self.findArduinoUnoPort()
        if unoPort:
            try:
                self.arduino = serial.Serial(
                    port='COM5', baudrate=9600, timeout=0.001)
                return 1

            except Exception:
                return 0

        return 0


if __name__ == '__main__':
    ex = Game()

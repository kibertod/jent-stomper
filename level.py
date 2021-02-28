from random import randint
import pygame
import sys
import os
from math import radians, sin, cos
from settings import *
from background import Background
from random import randint


angle_sides = dict()
for angle in range(360):
    angle_sides[angle] = abs(int(CUBE_SIDE * (abs(sin(radians(angle))) + abs(cos(radians(angle))))))


def load_image(name, colorkey=None):
    fullname = os.path.join('assets', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


front_sprites = pygame.sprite.Group()
back_sprites = pygame.sprite.Group()


class Cube(pygame.sprite.Sprite):
    cube = load_image("cube.png")

    def __init__(self, platform, *group):
        super().__init__(*group)
        self.platform = platform
        self.image = pygame.transform.scale(self.cube, (CUBE_SIDE, CUBE_SIDE))
        self.rect = self.image.get_rect()
        self.y = platform.y
        self.speed_y = 0
        self.angle = 0
        self.acceleration_y = 0
        self.speed_x = platform.speed
        self.acceleration_x = platform.acceleration
        self.x = platform.x + platform.width // 2 - CUBE_SIDE / 2
        self.rect.x = self.x
        self.rect.y = SCREEN_HEIGHT - self.y - CUBE_SIDE * 2

    def update(self, height):
        self.rect.x = self.x
        self.rect.y = SCREEN_HEIGHT - self.y - CUBE_SIDE - PLATFORM_HEIGHT + height

    def move(self, height, timelapce):
        if self.platform:
            self.acceleration_x = self.platform.acceleration
            self.speed_x = self.platform.speed
            x = self.x + self.speed_x
            if 0 <= x <= SCREEN_WIDTH - CUBE_SIDE:
                self.x = x
        else:
            self.speed_y = self.speed_y + self.acceleration_y / timelapce
            self.acceleration_x //= 2 * timelapce
            self.y += self.speed_y / timelapce
            x = (self.x + self.speed_x / timelapce)
            if x + CUBE_SIDE >= SCREEN_WIDTH or x <= 0:
                self.speed_x, self.acceleration_x = -self.speed_x, -self.acceleration_x
            self.x += self.speed_x / timelapce
            self.angle = int((abs(self.speed_x) + self.speed_y) * 10) % 360
        self.image = pygame.transform.rotate(self.cube, self.angle)
        side = angle_sides[self.angle]
        self.image = pygame.transform.scale(self.image, (side, side))
        self.update(height)

    def jump(self):
        if self.platform:
            self.speed_x = self.platform.speed * 2
            if self.platform.speed > 0:
                self.acceleration_x = -0.5
            else:
                self.acceleration_x = 0.5
            self.speed_y = JUMP_START_SPEED
            self.acceleration_y = FALL_ACCELERATION
            self.platform = 0

    def stand(self, platform):
        self.speed_x = platform.speed
        self.y = platform.y
        if self.angle < 45 or self.angle > 315:
            self.angle = 0
        elif 45 < self.angle < 135:
            self.angle = 90
        elif 135 < self.angle < 225:
            self.angle = 180
        else:
            self.angle = 270
        self.speed_y, self.acceleration_y = 0, 0
        self.acceleration_x = platform.acceleration
        self.platform = platform

    def stomp(self):
        self.speed_y = STOMP_SPEED
        self.speed_x = 0
        self.acceleration_x = 0


class Platform:
    def __init__(self, score):
        self.y = 100 + PLATFORMS_GAP * score
        self.score = score
        self.width = max((int(PLATFORM_START_WIDTH - score * 5), PLATFORM_HEIGHT))
        self.x = 0
        self.speed = 0
        if self.score:
            self.acceleration = 0.1 + (score / 40) * randint(1, 4)
        else:
            self.acceleration = 0
            self.x = SCREEN_WIDTH / 2 - self.width / 2

    def move(self, timelapce):
        if self.x + self.width // 2 >= SCREEN_WIDTH / 2:
            self.speed -= self.acceleration / timelapce
        else:
            self.speed += self.acceleration / timelapce
        if self.x + self.speed / timelapce <= 0 or self.x + self.speed / timelapce >= SCREEN_WIDTH:
            self.speed = 0
        self.x += self.speed / timelapce


class Level:
    def __init__(self, screen):
        self.score = 0
        self.height = 0
        self.started = False
        self.platforms = [Platform(i) for i in range(5)]
        self.cube = None
        self.screen = screen
        self.cube = Cube(self.platforms[0], front_sprites)
        self.background = Background(back_sprites)
        self.timelapce_timer = 0
        self.shake_timer = 0

    def restart(self):
        self.score = 0
        self.height = 0
        self.started = False
        self.platforms = [Platform(i) for i in range(5)]
        self.cube.stand(self.platforms[0])
        self.background = Background(back_sprites)
        self.timelapce_timer = 0
        self.shake_timer = 0
        self.cube.x = self.platforms[0].x + self.platforms[0].width // 2 - CUBE_SIDE / 2

    def move(self, timelapce):
        if timelapce and self.timelapce_timer == 2:
            self.background.update()
            self.timelapce_timer = 0
        elif timelapce:
            self.timelapce_timer += 1
        else:
            self.background.update()
        if timelapce and not self.cube.platform:
            timelapce = 5
        else:
            timelapce = 1
        if self.started:
            self.height = max((self.height + 1, self.cube.y + CUBE_SIDE * 2 - SCREEN_HEIGHT))
        for platform in self.platforms:
            platform.move(timelapce)
        self.platforms = list(filter(lambda x: x.y + PLATFORM_HEIGHT >= self.height, self.platforms))
        if self.cube.platform not in self.platforms and self.cube.platform:
            self.cube.jump()
            self.cube.speed_y = 0
        if len(self.platforms) < ACTIVE_PLATFORMS_COUNT:
            self.platforms += [Platform(self.platforms[-1].score + 1)]
        self.cube.move(self.height, timelapce)
        if self.cube.speed_y < 0:
            for platform in self.platforms:
                if abs(platform.y - self.cube.y) < -self.cube.speed_y and\
                   platform.x - CUBE_SIDE <= self.cube.x <= platform.x + platform.width:
                    self.cube.stand(platform)
                    self.shake_timer += 10
                    self.score = platform.score
                    break
        if self.cube.y + CUBE_SIDE * 2 < self.height:
            self.restart()

    def new_frame(self):
        if self.shake_timer:
            self.shake_timer -= 1
            shake = (randint(-15, 15), randint(-15, 15))
        else:
            shake = (0, 0)
        self.background.rect.x += shake[0]
        self.background.rect.y += shake[1]
        back_sprites.draw(self.screen)
        self.background.rect.x -= shake[0]
        self.background.rect.y -= shake[1]
        for platform in self.platforms:
            pygame.draw.rect(self.screen, "white", (platform.x - 1 + shake[0],
                                                    SCREEN_HEIGHT - platform.y - PLATFORM_HEIGHT + self.height - 1 + shake[1],
                                                    platform.width + 2, PLATFORM_HEIGHT + 2))
            pygame.draw.rect(self.screen, "black", (platform.x + shake[0],
                                                    SCREEN_HEIGHT - platform.y - PLATFORM_HEIGHT + self.height + shake[1],
                                                    platform.width, PLATFORM_HEIGHT))
        self.cube.rect.x += shake[0]
        self.cube.rect.y += shake[1]
        front_sprites.draw(self.screen)
        self.cube.rect.x -= shake[0]
        self.cube.rect.y -= shake[1]
        font = pygame.font.SysFont("sans-serif", 36)
        score = font.render(str(self.score), True, (255, 255, 255))
        if not self.started:
            start = font.render("click to start", True, (255, 255, 255))
            rect = start.get_rect()
            rect.x = SCREEN_WIDTH / 2 - rect.width / 2
            rect.y = SCREEN_HEIGHT / 2 - rect.height / 2
            self.screen.blit(start, rect)
        self.screen.blit(score, (10, 10))

import pygame
import sys
import os


def load_image(name, colorkey=None):
    fullname = os.path.join('assets', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Background(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.sheet = load_image("background.png")
        self.frame = -1
        self.update()

    def update(self):
        self.frame = (self.frame + 1) % 29
        self.image = self.sheet.subsurface(pygame.Rect(800 * self.frame, 0, 800, 600))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

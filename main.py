import pygame
import level
from settings import *
from datetime import timedelta, datetime


if __name__ == '__main__':
    pygame.init()
    size = width, height = SCREEN_WIDTH, SCREEN_HEIGHT
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    running = True
    level = level.Level(screen)
    timelapce = False
    timelapce_end = None
    pygame.display.set_caption("JENT STOMPER")
    pygame.mixer.music.load("assets/vector.mp3")
    pygame.mixer.music.play(10, 8)
    pygame.mixer.music.set_volume(0.05)
    while running:
        screen.fill((0, 0, 0))
        level.move(timelapce)
        level.new_frame()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                level.started = True
                if level.cube.platform:
                    level.cube.jump()
                else:
                    timelapce = True
                    timelapce_end = datetime.now() + timedelta(seconds=0.75)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if timelapce:
                    level.cube.stomp()
                    level.shake_timer += 20
                    timelapce_end = None
                timelapce = False
        if timelapce_end:
            if timelapce_end <= datetime.now():
                level.shake_timer += 20
                level.cube.stomp()
                timelapce = False
                timelapce_end = None
        clock.tick(60)
        pygame.display.flip()
    else:
        pygame.quit()

import numpy as np
import pygame

from .components.cube import Cube3D


def main_loop():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True

    cube = Cube3D(640, 360, 100)
    dt = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))

        cube.rotate(dt * 2, dt, 0)

        cube.render(screen)

        pygame.display.flip()

        dt += clock.tick(60) / 1000

    pygame.quit()

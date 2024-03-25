import pygame
import sys
from config.settings import *
from config.debug import debug
from src.level import Level

import warnings
warnings.filterwarnings('ignore')


class Game:
    def __init__(self):

        # general setup
        pygame.init()
        pygame.display.set_caption('The Office')
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        self.clock = pygame.time.Clock()

        self.level = Level()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill((20, 27, 27))
            self.level.run()

            # Debug
            # debug(f"FPS: {self.clock.get_fps() :.2f}")

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()

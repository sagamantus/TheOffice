import socket
import threading
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
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))        
        # threading.Thread(target=self.level.other_players_add, args=(client_socket,)).run()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill((20, 27, 27))
            
            self.level.run(client_socket)

            # Debug
            # debug(f"FPS: {self.clock.get_fps() :.2f}")

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()

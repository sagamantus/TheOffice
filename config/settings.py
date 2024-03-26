import csv
import pygame

# game setup
WIDTH    = 1280	
HEIGTH   = 720
FPS      = 60
DATA_FPS = 120
TILESIZE = 64

CHARACTER = 'Eskimo'
USERNAME = 'sagamantus'

SERVER_HOST = '192.168.137.1'
SERVER_PORT = 12345

pygame.font.init()

with open('./graphic/world_Hidden.csv', 'r') as f:
    WORLD_MAP = list(csv.reader(f))
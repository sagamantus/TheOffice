import csv
import pygame

# game setup
WIDTH    = 1280	
HEIGTH   = 720
FPS      = 60
TILESIZE = 64

CHARACTER = 'Eskimo'
USERNAME = 'sagamantus'

pygame.font.init()

with open('./graphic/world_Hidden.csv', 'r') as f:
    WORLD_MAP = list(csv.reader(f))
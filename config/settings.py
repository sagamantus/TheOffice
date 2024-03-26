import csv
import pygame
import pyaudio

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
AUDIO_PORT  = 50007

CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 20000
RECORD_SECONDS = 4000

pygame.font.init()

with open('./graphic/world_Hidden.csv', 'r') as f:
    WORLD_MAP = list(csv.reader(f))
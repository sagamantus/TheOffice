import pickle
import socket
import threading
import time
import pygame
from config.settings import *

from src.other_player import OtherPlayer
from src.tile import Tile
from src.player import Player
from src.websocket import connect_host

from config.debug import debug


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):

        # general setup
        super().__init__()
        # get the display surface
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_width()//2
        self.half_height = self.display_surface.get_height()//2
        self.offset = pygame.math.Vector2()

        # Creating floor
        self.floor_surface = pygame.image.load('./graphic/world.png')
        self.floor_surface = pygame.transform.scale(
            self.floor_surface, (self.floor_surface.get_width() * (TILESIZE//16), self.floor_surface.get_height() * (TILESIZE//16))).convert()
        self.floor_rect = self.floor_surface.get_rect(topleft=(0, 0))

        self.chairs = pygame.image.load('./graphic/Chairs.png')
        self.chairs = pygame.transform.scale(
            self.chairs, (self.chairs.get_width() * (TILESIZE//16), self.chairs.get_height() * (TILESIZE//16))).convert_alpha()

        # Creating walls
        self.wall_surface = pygame.image.load('./graphic/Walls.png')
        self.wall_surface = pygame.transform.scale(
            self.wall_surface, (self.wall_surface.get_width() * (TILESIZE//16), self.wall_surface.get_height() * (TILESIZE//16))).convert_alpha()

        # Creating items
        self.items_surface = pygame.image.load('./graphic/Items.png')
        self.items_surface = pygame.transform.scale(
            self.items_surface, (self.items_surface.get_width() * (TILESIZE//16), self.items_surface.get_height() * (TILESIZE//16))).convert_alpha()
        
        self.shadow = pygame.image.load('./graphic/Shadow.png')
        self.shadow = pygame.transform.scale(
            self.shadow, (self.shadow.get_width() * (TILESIZE//16), self.shadow.get_height() * (TILESIZE//16))).convert_alpha()
        
    def custom_draw(self, player):

        # getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # Drawing floor
        floor_offset_position = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surface, floor_offset_position)
        self.display_surface.blit(self.chairs, floor_offset_position)

        # If player's last direction going UP add walls and items first
        if player.last_direction_y < 0: self.display_surface.blit(self.wall_surface, floor_offset_position)
        if player.last_direction_y < 0: self.display_surface.blit(self.items_surface, floor_offset_position)

        self.display_surface.blit(self.shadow, self.shadow.get_rect(center = player.rect.center).topleft-pygame.math.Vector2(self.offset.x, self.offset.y - (TILESIZE//2)))

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_postion = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_postion)


        # If player's last direction was DOWN add walls and items after player
        if player.last_direction_y > 0: self.display_surface.blit(self.wall_surface, floor_offset_position)
        if player.last_direction_y > 0: self.display_surface.blit(self.items_surface, floor_offset_position)

        # self.face_box = pygame.image.load(f'./graphic/Characters/{CHARACTER}/Faceset.png').convert_alpha()
        # self.face_box = pygame.transform.scale(
        #     self.face_box, (self.face_box.get_width() * max(1, TILESIZE//32), self.face_box.get_height() * max(1, TILESIZE//32))).convert_alpha()
        # self.display_surface.blit(self.face_box, (16,16))

        outlineSurf = pygame.font.Font('./graphic/NormalFont.ttf', 16).render(USERNAME, True, (255, 255, 255), (0, 0, 0))
        self.display_surface.blit(outlineSurf, outlineSurf.get_rect(center = player.rect.center).topleft-pygame.math.Vector2(self.offset.x, self.offset.y + TILESIZE - (TILESIZE//10)))


class Level:
    def __init__(self) -> None:

        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # group for sprites that will be drawn (only group that draws sprites)
        self.visible_sprites = YSortCameraGroup()
        # group for sprites that the player can collide with
        self.obstacle_sprites = pygame.sprite.Group()

        self.shadow = pygame.image.load('./graphic/Shadow.png')
        self.shadow = pygame.transform.scale(
            self.shadow, (self.shadow.get_width() * (TILESIZE//16), self.shadow.get_height() * (TILESIZE//16))).convert_alpha()
        
        self.other_players = {}

        # sprite setup
        self.create_map()

    def create_map(self):
        for row_index, row in enumerate(WORLD_MAP):
            for column_index, column in enumerate(row):
                x = column_index * TILESIZE
                y = row_index * TILESIZE
                if column == '48':
                    Tile((x, y), [self.obstacle_sprites], 'invisible')
                if column == '58':
                    self.player = Player(
                        (x, y), self.obstacle_sprites, [self.visible_sprites])
        
    def run(self, client_socket):
        # update and draw the game
        client_socket.setblocking(False)
        try:
            data = client_socket.recv(8192)
            data = pickle.loads(data)
            if data.get('disconnect', None) != None:
                self.other_players[data["disconnect"]].kill()
                del self.other_players[data["disconnect"]]   
            elif data['client_address'] not in self.other_players:
                self.other_players[data["client_address"]] = OtherPlayer(data['name'], data['position'], data['status'], data['direction'], data['frame_index'], data['hitbox'], data['character'], self.obstacle_sprites, [self.visible_sprites])
            else:
                self.other_players[data["client_address"]].position = data['position']
                self.other_players[data["client_address"]].direction = data['direction']
                self.other_players[data["client_address"]].status = data['status']
                self.other_players[data["client_address"]].frame_index = data['frame_index']
                self.other_players[data["hitbox"]].frame_index = data['hitbox']
        except Exception as e:
            pass
        
        self.visible_sprites.custom_draw(self.player)
        client_socket.send(pickle.dumps({'name': USERNAME, 'position': self.player.rect.topleft, 'status': self.player.status, 'direction': self.player.direction, 'frame_index': self.player.frame_index, 'hitbox': self.player.hitbox, 'character': CHARACTER}))
        self.visible_sprites.update()

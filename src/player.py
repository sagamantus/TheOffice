import pygame
from config.settings import *
from src.entity import Entity

import warnings
warnings.filterwarnings('ignore')


class Player(Entity):
    def __init__(self, position, obstacle_sprites, groups) -> None:
        super().__init__(groups)
        self.image = pygame.image.load('./graphic/idle.png').convert_alpha()
        self.image = self.image.subsurface((0, 0, 16, 16))  # cropping
        self.image = pygame.transform.scale(
            self.image, (TILESIZE, TILESIZE))  # resizing to tilesize
        self.position = position
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(0, -TILESIZE//2.5)

        self.character = CHARACTER

        self.import_player_assets(self.character)
        self.status = 'down_idle'

        # movement
        self.last_direction_y = 1

        self.obstacle_sprites = obstacle_sprites

    def import_player_assets(self, character):
        image = pygame.image.load(f'./graphic/Characters/{character}/SpriteSheet.png').convert_alpha()
        self.animations = {
                            'down':[image.subsurface((0, i, 16, 16)) for i in range(0, 49, 16)],
                            'up': [image.subsurface((16, i, 16, 16)) for i in range(0, 49, 16)],
                            'left': [image.subsurface((32, i, 16, 16)) for i in range(0, 49, 16)],
                            'right': [image.subsurface((48,i, 16, 16)) for i in range(0, 49, 16)],
                           }
    
        self.animations['down_idle'] = [self.animations['down'][0]]
        self.animations['up_idle'] = [self.animations['up'][0]]
        self.animations['left_idle'] = [self.animations['left'][0]]
        self.animations['right_idle'] = [self.animations['right'][0]]

    def input(self):
        keys = pygame.key.get_pressed()

        # movement
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
            self.last_direction_y = -1
            self.status = 'up'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
            self.last_direction_y = 1
            self.status = 'down'
        else:
            self.direction.y = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.status = 'left'
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.status = 'right'
        else:
            self.direction.x = 0
    
    def get_status(self):
        # idle status
        if self.direction.x == 0 and self.direction.y == 0 and not self.status.endswith('_idle'):
            self.status = self.status + '_idle'

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

    def animate(self):
        animations = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animations):
            self.frame_index = 0

        self.image = pygame.transform.scale(
            animations[int(self.frame_index)].convert_alpha(), (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect(center = self.hitbox.center)

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)

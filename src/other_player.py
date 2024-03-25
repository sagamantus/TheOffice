import pygame
from config.settings import *
from src.entity import Entity

class OtherPlayer(Entity):
    def __init__(self, name, pos, status, direction, frame_index, hitbox, character, obstacle_sprites, groups):
        
        super().__init__(groups)
        self.sprite_type = 'other_player'
        self.character = character
        
        # graphics setup
        self.import_player_assets(character)
        self.status = status
        self.image = self.animations[self.status][self.frame_index]
        self.frame_index = frame_index
         
        # movement
        self.direction = direction
        self.position = pos
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = hitbox
        self.obstacle_sprites = obstacle_sprites
        
        self.name = name
        
        self.shadow = pygame.image.load('./graphic/Shadow.png')
        self.shadow = pygame.transform.scale(
            self.shadow, (self.shadow.get_width() * (TILESIZE//16), self.shadow.get_height() * (TILESIZE//16))).convert_alpha()
        
        self.display_surface = pygame.display.get_surface()
    
    def import_player_assets(self, character):
        image = pygame.image.load(f'./graphic/Characters/{character}/SpriteSheet.png').convert_alpha()
        self.animations = {
                            'down':[pygame.transform.scale(image.subsurface((0, i, 16, 16)), (TILESIZE, TILESIZE)) for i in range(0, 49, 16)],
                            'up': [pygame.transform.scale(image.subsurface((16, i, 16, 16)), (TILESIZE, TILESIZE)) for i in range(0, 49, 16)],
                            'left': [pygame.transform.scale(image.subsurface((32, i, 16, 16)), (TILESIZE, TILESIZE)) for i in range(0, 49, 16)],
                            'right': [pygame.transform.scale(image.subsurface((48,i, 16, 16)), (TILESIZE, TILESIZE)) for i in range(0, 49, 16)],
                           }
    
        self.animations['down_idle'] = [self.animations['down'][0]]
        self.animations['up_idle'] = [self.animations['up'][0]]
        self.animations['left_idle'] = [self.animations['left'][0]]
        self.animations['right_idle'] = [self.animations['right'][0]]
                
    def animate(self):
        animations = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animations):
            self.frame_index = 0

        self.image = animations[int(self.frame_index)].convert_alpha()
        self.rect = self.image.get_rect(center = self.hitbox.center)
        
                
    def update(self):
        self.animate()
        self.move(self.speed)
        
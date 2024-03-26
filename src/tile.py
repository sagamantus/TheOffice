import pygame
from config.settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(
        self,
        position,
        groups,
        sprite_type,
        surface=pygame.Surface((TILESIZE, TILESIZE)),
        inflate=False,
    ) -> None:
        super().__init__(groups)
        self.image = surface
        self.sprite_type = sprite_type
        self.rect = self.image.get_rect(topleft=position)
        if inflate:
            self.hitbox = self.rect.inflate(0, -TILESIZE // 3)
        else:
            self.hitbox = self.rect.inflate(0, 0)

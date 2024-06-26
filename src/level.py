import pickle
import socket
import threading
import pygame
import pyaudio
from config.settings import *

from src.other_player import OtherPlayer
from src.tile import Tile
from src.player import Player

from config.debug import debug


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):

        # general setup
        super().__init__()
        # get the display surface
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_width() // 2
        self.half_height = self.display_surface.get_height() // 2
        self.offset = pygame.math.Vector2()

        # Creating floor
        self.floor_surface = pygame.image.load("./graphic/world.png")
        self.floor_surface = pygame.transform.scale(
            self.floor_surface,
            (
                self.floor_surface.get_width() * (TILESIZE // 16),
                self.floor_surface.get_height() * (TILESIZE // 16),
            ),
        ).convert()
        self.floor_rect = self.floor_surface.get_rect(topleft=(0, 0))

        self.chairs = pygame.image.load("./graphic/Chairs.png")
        self.chairs = pygame.transform.scale(
            self.chairs,
            (
                self.chairs.get_width() * (TILESIZE // 16),
                self.chairs.get_height() * (TILESIZE // 16),
            ),
        ).convert_alpha()

        # Creating walls
        self.wall_surface = pygame.image.load("./graphic/Walls.png")
        self.wall_surface = pygame.transform.scale(
            self.wall_surface,
            (
                self.wall_surface.get_width() * (TILESIZE // 16),
                self.wall_surface.get_height() * (TILESIZE // 16),
            ),
        ).convert_alpha()

        # Creating items
        self.items_surface = pygame.image.load("./graphic/Items.png")
        self.items_surface = pygame.transform.scale(
            self.items_surface,
            (
                self.items_surface.get_width() * (TILESIZE // 16),
                self.items_surface.get_height() * (TILESIZE // 16),
            ),
        ).convert_alpha()

        self.shadow = pygame.image.load("./graphic/Shadow.png")
        self.shadow = pygame.transform.scale(
            self.shadow,
            (
                self.shadow.get_width() * (TILESIZE // 16),
                self.shadow.get_height() * (TILESIZE // 16),
            ),
        ).convert_alpha()

    def custom_draw(self, player):

        # getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # Drawing floor
        floor_offset_position = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surface, floor_offset_position)
        self.display_surface.blit(self.chairs, floor_offset_position)

        # If player's last direction going UP add walls and items first
        if player.last_direction_y < 0:
            self.display_surface.blit(self.wall_surface, floor_offset_position)
        if player.last_direction_y < 0:
            self.display_surface.blit(self.items_surface, floor_offset_position)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            if type(sprite) == OtherPlayer:
                self.display_surface.blit(
                    self.shadow,
                    self.shadow.get_rect(center=sprite.rect.center).topleft
                    - pygame.math.Vector2(
                        self.offset.x, self.offset.y - (TILESIZE // 2)
                    ),
                )
                outlineSurf = pygame.font.Font("./graphic/NormalFont.ttf", 16).render(
                    sprite.name, True, (255, 255, 255), (0, 0, 0)
                )
                self.display_surface.blit(
                    outlineSurf,
                    outlineSurf.get_rect(center=sprite.rect.center).topleft
                    - pygame.math.Vector2(
                        self.offset.x, self.offset.y + TILESIZE - (TILESIZE // 10)
                    ),
                )
            if type(sprite) == Player:
                self.display_surface.blit(
                    self.shadow,
                    self.shadow.get_rect(center=sprite.rect.center).topleft
                    - pygame.math.Vector2(
                        self.offset.x, self.offset.y - (TILESIZE // 2)
                    ),
                )
            offset_postion = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_postion)
        outlineSurf = pygame.font.Font("./graphic/NormalFont.ttf", 16).render(
            USERNAME, True, (255, 255, 255), (0, 0, 0)
        )
        self.display_surface.blit(
            outlineSurf,
            outlineSurf.get_rect(center=player.rect.center).topleft
            - pygame.math.Vector2(
                self.offset.x, self.offset.y + TILESIZE - (TILESIZE // 10)
            ),
        )

        # If player's last direction was DOWN add walls and items after player
        if player.last_direction_y > 0:
            self.display_surface.blit(self.wall_surface, floor_offset_position)
        if player.last_direction_y > 0:
            self.display_surface.blit(self.items_surface, floor_offset_position)

        # self.face_box = pygame.image.load(f'./graphic/Characters/{CHARACTER}/Faceset.png').convert_alpha()
        # self.face_box = pygame.transform.scale(
        #     self.face_box, (self.face_box.get_width() * max(1, TILESIZE//32), self.face_box.get_height() * max(1, TILESIZE//32))).convert_alpha()
        # self.display_surface.blit(self.face_box, (16,16))


class Level:
    def __init__(self) -> None:

        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # group for sprites that will be drawn (only group that draws sprites)
        self.visible_sprites = YSortCameraGroup()
        # group for sprites that the player can collide with
        self.obstacle_sprites = pygame.sprite.Group()

        self.shadow = pygame.image.load("./graphic/Shadow.png")
        self.shadow = pygame.transform.scale(
            self.shadow,
            (
                self.shadow.get_width() * (TILESIZE // 16),
                self.shadow.get_height() * (TILESIZE // 16),
            ),
        ).convert_alpha()

        self.other_players = {}

        # sprite setup
        self.create_map()

        p = pyaudio.PyAudio()

        self.stream_audio_in = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        self.stream_audio_out = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK,
        )

        s_audio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_audio.connect((SERVER_HOST, AUDIO_PORT))
        send_audio_thread = threading.Thread(
            target=self.send_audio_data,
            args=(s_audio, self.stream_audio_in),
            daemon=True,
        )
        receive_audio_thread = threading.Thread(
            target=self.receive_audio_data,
            args=(s_audio, self.stream_audio_out),
            daemon=True,
        )
        send_audio_thread.start()
        receive_audio_thread.start()

    def send_audio_data(self, sock, stream):
        try:
            while True:
                pos = self.player.rect.topleft
                data = stream.read(CHUNK).decode(encoding="latin-1")
                sock.sendall(pickle.dumps([pos, data]))
        except Exception as e:
            print("Error sending audio data:", e)

    def receive_audio_data(self, sock, stream):
        while True:
            try:
                data = sock.recv(2048)
                data = pickle.loads(data)
                if not data:
                    break
                # check same room
                pos = data[0]
                data = data[1].encode(encoding="latin-1")
                if (
                    (
                        (64 <= pos[0] <= 512 and 883 <= pos[1] <= 1165)
                        and (
                            64 <= self.player.rect.topleft[0] <= 512
                            and 883 <= self.player.rect.topleft[1] <= 1165
                        )
                    )
                    or (
                        (64 <= pos[0] <= 512 and 51 <= pos[1] <= 525)
                        and (
                            64 <= self.player.rect.topleft[0] <= 512
                            and 51 <= self.player.rect.topleft[1] <= 525
                        )
                    )
                    or (
                        (640 <= pos[0] <= 1792 and 51 <= pos[1] <= 525)
                        and (
                            640 <= self.player.rect.topleft[0] <= 1792
                            and 51 <= self.player.rect.topleft[1] <= 525
                        )
                    )
                    or (
                        (640 <= pos[0] <= 1216 and 883 <= pos[1] <= 1165)
                        and (
                            640 <= self.player.rect.topleft[0] <= 1216
                            and 883 <= self.player.rect.topleft[1] <= 1165
                        )
                    )
                    or (
                        (1344 <= pos[0] <= 1792 and 883 <= pos[1] <= 1165)
                        and (
                            1344 <= self.player.rect.topleft[0] <= 1792
                            and 883 <= self.player.rect.topleft[1] <= 1165
                        )
                    )
                ):
                    stream.write(data)
            except Exception as e:
                print("Error receiving audio data:", e)

    def create_map(self):
        for row_index, row in enumerate(WORLD_MAP):
            for column_index, column in enumerate(row):
                x = column_index * TILESIZE
                y = row_index * TILESIZE
                if column == "48":
                    Tile((x, y), [self.obstacle_sprites], "invisible")
                if column == "58":
                    self.player = Player(
                        (x, y), self.obstacle_sprites, [self.visible_sprites]
                    )

    def run(self, client_socket):
        # update and draw the game
        client_socket.setblocking(False)
        try:
            data = client_socket.recv(1024)
            data = pickle.loads(data)
            if data.get("disconnect", None) != None:
                self.other_players[data["disconnect"]].kill()
                del self.other_players[data["disconnect"]]
            elif data["client_address"] not in self.other_players:
                self.other_players[data["client_address"]] = OtherPlayer(
                    data["name"],
                    data["position"],
                    data["status"],
                    data["direction"],
                    data["frame_index"],
                    data["hitbox"],
                    data["character"],
                    self.obstacle_sprites,
                    [self.visible_sprites],
                )
            else:
                self.other_players[data["client_address"]].position = data["position"]
                self.other_players[data["client_address"]].direction = data["direction"]
                self.other_players[data["client_address"]].status = data["status"]
                self.other_players[data["client_address"]].frame_index = data[
                    "frame_index"
                ]
                self.other_players[data["client_address"]].hitbox = data["hitbox"]
        except Exception as e:
            pass

        self.visible_sprites.custom_draw(self.player)
        client_socket.send(
            pickle.dumps(
                {
                    "name": USERNAME,
                    "position": self.player.rect.topleft,
                    "status": self.player.status,
                    "direction": self.player.direction,
                    "frame_index": self.player.frame_index,
                    "hitbox": self.player.hitbox,
                    "character": CHARACTER,
                }
            )
        )
        self.visible_sprites.update()

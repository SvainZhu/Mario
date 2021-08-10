import pygame
from .. import setup
from .. import tools
from .. import constants as C
from .powerup import create_powerup

class Box(pygame.sprite.Sprite):
    def __init__(self, x, y, box_type, group, name='box'):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.box_type = box_type
        self.group = group
        self.gravity = C.GRAVITY
        box_frame_rects = [(384, 0, 16, 16), (400, 0, 16, 16), (416, 0, 16, 16), (432, 0, 16, 16)]

        self.frame_rects = box_frame_rects
        self.frames = []
        for frame_rect in self.frame_rects:
            self.frames.append(tools.get_image(setup.GRAPHICS['tile_set'], *frame_rect, (0, 0, 0), C.BRICK_MULTI))

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.state = 'normal'
        self.timer = 0
        self.name = name

    def update(self):
        self.current_time = pygame.time.get_ticks()
        self.handle_states()

    def handle_states(self):
        if self.state == 'normal':
            self.normal()
        elif self.state == 'bumped':
            self.bumped()
        elif self.state == 'opened':
            self.opened()

    def normal(self):
        frame_durations = [500, 100, 100, 50]
        if self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index += 1
            self.frame_index %= 4
            self.timer = self.current_time
        self.image = self.frames[self.frame_index]


    def go_bumped(self):
        self.y_vel = -7
        self.state = 'bumped'


    def bumped(self):
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        self.frame_index = 3
        self.image = self.frames[self.frame_index]

        if self.rect.y > self.y:
            self.rect.y = self.y
            self.y_vel = 0
            self.state = 'open'

            # box_type 0, 1, 2, 3 分别对应了空箱子、金币、星星和蘑菇
            if self.box_type == 1:
                pass
            else:
                self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.box_type))

    def opened(self):
        pass



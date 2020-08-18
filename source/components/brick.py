import pygame
from .. import setup
from .. import tools
from .. import constants as C


class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, brick_type, color=None, name='brick'):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.brick_type = brick_type
        brown_frame_rects = [(16, 0, 16, 16), (48, 0, 16, 16)]
        blue_frame_rects = [(16, 32, 16, 16), (48, 32, 16, 16)]

        if not color:
            self.frame_rects = brown_frame_rects
        else:
            self.frame_rects = blue_frame_rects

        self.frames = []
        for frame_rect in self.frame_rects:
            self.frames.append(tools.get_image(setup.GRAPHICS['tile_set'], *frame_rect, (0, 0, 0), C.BRICK_MULTI))

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.name = name
        self.state = 'normal'
        self.gravity = C.GRAVITY

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
        pass


    def go_bumped(self):
        self.y_vel = -7
        self.state = 'bumped'


    def bumped(self):
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        if self.rect.y > self.y:
            self.rect.y = self.y
            self.y_vel = 0
            self.state = 'normal'

    def opened(self):
        pass



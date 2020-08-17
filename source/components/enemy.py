import pygame
from .. import setup
from .. import tools
from .. import constants as C



def create_enemy(enemy_data):
    enemy_type = enemy_data['type']
    x, y_bottom, direction, color = enemy_data['x'], enemy_data['y'], enemy_data['direction'], enemy_data['color']

    if enemy_type == 0:
        enemy = Goomba(x, y_bottom, direction, 'goomba', color)     # goomba：蘑菇怪
    elif enemy_type == 1:
        enemy = Koopa(x, y_bottom, direction, 'koopa', color)       # koopa：乌龟


    return enemy



class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y_bottom, direction, name, frame_rects):
        pygame.sprite.Sprite.__init__(self)
        self.direction = direction
        self.name = name
        self.frame_index = 0
        self.left_frames = []
        self.right_frames = []

        self.load_frames(frame_rects)
        if self.direction == 0:
            self.frames = self.left_frames
        else:
            self.frames = self.right_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y_bottom

        self.timer = 0
        if self.direction == 0:
            self.x_vel = -1 * C.ENEMY_SPEED
        else:
            self.x_vel = C.ENEMY_SPEED
        self.y_vel = 0
        self.gravity = C.GRAVITY
        self.state = 'walk'

    def load_frames(self, frame_rects):
        for frame_rect in frame_rects:
            left_frame = tools.get_image(setup.GRAPHICS['enemies'], *frame_rect, (0, 0, 0), C.ENEMY_MULTI)
            right_frame = pygame.transform.flip(left_frame, True, False)
            self.left_frames.append(left_frame)
            self.right_frames.append(right_frame)

    def update(self, level):
        self.current_time = pygame.time.get_ticks()
        self.handle_states()
        self.update_position(level)

    def handle_states(self):
        if self.state == 'walk':
            self.walk()
        elif self.state == 'fall':
            self.fall()
        elif self.state == 'die':
            self.die()
        elif self.state == 'trampled':
            self.trampled()

        if self.direction:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    def walk(self):
        if self.current_time - self.timer > 125:
            self.frame_index = (self.frame_index + 1) % 2
            self.timer = self.current_time
            self.image = self.frames[self.frame_index]

    def fall(self):
        if self.y_vel < 10:
            self.y_vel += self.gravity

    def update_position(self, level):
        self.rect.x += self.x_vel
        self.check_x_collisions(level)
        self.rect.y += self.y_vel
        self.check_y_collisions(level)

    def check_x_collisions(self, level):
        item = pygame.sprite.spritecollideany(self, level.ground_items_group)
        if item:
            if self.direction == 0:
                self.direction = 1
            else:
                self.direction = 0
            self.x_vel *= -1

    def check_y_collisions(self, level):
        group = pygame.sprite.Group(level.ground_items_group, level.brick_group, level.box_group)
        item = pygame.sprite.spritecollideany(self, group)
        if item:
            if self.rect.top < item.rect.top:
                self.rect.bottom = item.rect.top
                self.y_vel = 0
                self.state = 'walk'

        level.check_fall(self)





class Goomba(Enemy):
    def __init__(self, x, y_bottom, direction, name, color):
        pygame.sprite.Sprite.__init__(self)
        brown_frame_rects = [(0, 16, 16, 16), (16, 16, 16, 16), (32, 16, 16, 16)]
        blue_frame_rects = [(0, 48, 16, 16), (16, 48, 16, 16), (32, 48, 16, 16)]

        if not color:
            frame_rects = brown_frame_rects
        else:
            frame_rects = blue_frame_rects

        Enemy.__init__(self, x, y_bottom, direction, name, frame_rects)


class Koopa(Enemy):
    def __init__(self, x, y_bottom, direction, name, color):
        pygame.sprite.Sprite.__init__(self)
        brown_frame_rects = [(96, 9, 16, 22), (122, 9, 16, 22), (160, 9, 16, 22)]
        blue_frame_rects = [(96, 72, 16, 22), (122, 72, 16, 22), (160, 72, 16, 22)]

        if not color:
            frame_rects = brown_frame_rects
        else:
            frame_rects = blue_frame_rects

        Enemy.__init__(self, x, y_bottom, direction, name, frame_rects)



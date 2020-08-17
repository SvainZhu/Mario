# -*- coding: utf-8 -*-
import pygame
import os
import json
from ..components import info, player, stuff
from .. import tools, setup
from .. import constants as C


class Level:
    def start(self, game_info):
        self.game_info = game_info
        self.finished = False
        self.next = 'game_over'
        self.info = info.Info('level', self.game_info)
        self.load_map_data()
        self.setup_background()
        self.setup_start_position()
        self.setup_player()
        self.setup_ground_items()

    def load_map_data(self):
        file_name = 'level_1.json'
        file_path = os.path.join('source/data/maps', file_name)
        with open(file_path) as f:
            self.map_data = json.load(f)

    def setup_background(self):
        self.image_name = self.map_data['image_name']
        self.background = setup.GRAPHICS[self.image_name]
        rect = self.background.get_rect()
        self.background = pygame.transform.scale(self.background, (int(rect.width * C.BG_MULTI),
                                                                 int(rect.height * C.BG_MULTI)))
        self.background_rect = self.background.get_rect()
        self.game_window = setup.SCREEN.get_rect()
        self.game_ground = pygame.Surface((self.background_rect.width, self.background_rect.height))

    # 设置画面的起始值、终止值，玩家的起始x值和y值
    def setup_start_position(self):
        self.positons = []
        for data in self.map_data['maps']:
            self.positons.append((data['start_x'], data['end_x'], data['player_x'], data['player_y']))
        self.start_x, self.end_x, self.player_x, self.player_y = self.positons[0]

    def setup_player(self):
        self.player = player.Player('mario')
        self.player.rect.x = self.start_x + self.player_x
        self.player.rect.bottom = self.player_y

    def setup_ground_items(self):
        self.ground_items_group = pygame.sprite.Group()
        for name in ['ground', 'pipe', 'step']:
            for item in self.map_data[name]:
                self.ground_items_group.add(stuff.Item(item['x'], item['y'], item['width'], item['height'], name))


    def update(self, surface, keys):

        self.current_time = pygame.time.get_ticks()
        self.player.update(keys)

        if self.player.dead:
            if self.current_time - self.player.death_timer > 3000:
                self.finished = True
                self.update_game_info()
        else:
            self.update_player_position()
            self.check_if_go_die()
            self.update_game_window()
            self.info.update()
        self.draw(surface)


    def update_player_position(self):
        # x坐标碰撞检测
        self.player.rect.x += self.player.x_vel
        if self.player.rect.x < self.game_window.x:
            self.player.rect.x = self.game_window.x
        elif self.player.rect.right > self.end_x:
            self.player.rect.right = self.end_x
        self.check_x_collision()

        # y坐标碰撞检测
        self.player.rect.y += self.player.y_vel
        self.check_y_collision()

    # x坐标碰撞检测
    def check_x_collision(self):
        ground_item = pygame.sprite.spritecollideany(self.player, self.ground_items_group)
        if ground_item:
            self.adjust_player_x(ground_item)

    # x坐标位置调整
    def adjust_player_x(self, item):
        if self.player.rect.x < item.rect.x:
            self.player.rect.right = item.rect.left
        else:
            self.player.rect.left = item.rect.right
        self.player.x_vel = 0

    # y坐标碰撞检测
    def check_y_collision(self):
        ground_item = pygame.sprite.spritecollideany(self.player, self.ground_items_group)
        if ground_item:
            self.adjust_player_y(ground_item)
        self.check_fall(self.player)

    def adjust_player_y(self, item):

        if self.player.rect.bottom < item.rect.bottom:
            self.player.rect.bottom = item.rect.top
            self.player.y_vel = 0
            self.player.states = 'fall'
            self.player.states = 'walk'
        else:
            self.player.y_vel = 8
            self.player.rect.top = item.rect.bottom
            self.player.states = 'fall'

    def check_fall(self, item):
        item.rect.y += 1
        collided = pygame.sprite.spritecollideany(item, self.ground_items_group)
        if not collided and item.states != 'jump':
            item.states = 'fall'

        item.rect.y -=1


    def check_if_go_die(self):
        if self.player.rect.y > C.SCREEN_H:
            self.player.go_die()

    def update_game_info(self):
        if self.player.dead:
            self.game_info['lives'] -= 1
        if self.game_info['lives'] == 0:
            self.next = 'game_over'
        else:
            self.next = 'load_screen'

    def update_game_window(self):
        third = self.game_window.x + self.game_window.width / 3
        if self.player.x_vel > 0 and self.player.rect.centerx > third and self.game_window.right < self.end_x :
            self.game_window.x += self.player.x_vel


    def draw(self, surface):
        self.game_ground.blit(self.background, self.game_window, self.game_window)
        self.game_ground.blit(self.player.image, self.player.rect)
        surface.blit(self.game_ground, (0, 0), self.game_window)
        self.info.draw(surface)
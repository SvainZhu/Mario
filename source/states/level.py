# -*- coding: utf-8 -*-
import pygame
import os
import json
from ..components import info, player, stuff, brick, box, enemy
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
        self.setup_bricks()
        self.setup_boxs()
        self.setup_enemies()
        self.setup_checkpoints()

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

    def setup_bricks(self):
        self.brick_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()  ## 金币道具组
        self.powerup_group = pygame.sprite.Group()  ## 状态增强道具组

        if 'brick' in self.map_data:
            for brick_data in self.map_data['brick']:
                x, y = brick_data['x'], brick_data['y']
                brick_type = brick_data['type']
                if brick_type == 0:

                    if 'brick_num' in brick_data:
                        # TODO batch bricks
                        # brick_num = brick_data['brick_num']
                        pass
                    else:
                        self.brick_group.add(brick.Brick(x, y, brick_type, None))
                elif brick_type == 1:
                    self.brick_group.add(brick.Brick(x, y, brick_type, self.coin_group))
                else:
                    self.brick_group.add(brick.Brick(x, y, brick_type, self.powerup_group))


    def setup_boxs(self):
        self.box_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()         ## 金币道具组
        self.powerup_group = pygame.sprite.Group()      ## 状态增强道具组


        if 'box' in self.map_data:
            for box_data in self.map_data['box']:
                x, y = box_data['x'], box_data['y']
                box_type = box_data['type']
                if box_type == 1:
                    self.box_group.add(box.Box(x, y, box_type, self.coin_group))
                else:
                    self.box_group.add(box.Box(x, y, box_type, self.powerup_group))


    def setup_enemies(self):
        self.die_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.shell_group = pygame.sprite.Group()
        self.enemy_group_dict = {}
        for enemy_group_data in self.map_data['enemy']:
            group = pygame.sprite.Group()
            for enemy_group_id, enemy_list in enemy_group_data.items():
                for enemy_data in enemy_list:
                    group.add(enemy.create_enemy(enemy_data))
                self.enemy_group_dict[enemy_group_id] = group

    def setup_checkpoints(self):
        self.checkpoint_group = pygame.sprite.Group()
        for item in self.map_data['checkpoint']:
            x, y, width, height = item['x'], item['y'], item['width'], item['height']
            checkpoint_type = item['type']
            enemy_groupid = item.get('enemy_groupid')
            self.checkpoint_group.add((stuff.Checkpoint(x, y, width, height, checkpoint_type, enemy_groupid)))

    def check_checkpoint(self):
        checkpoint = pygame.sprite.spritecollideany(self.player, self.checkpoint_group)
        if checkpoint:
            if checkpoint.checkpoint_type == 0:
                self.enemy_group.add(self.enemy_group_dict[(str(checkpoint.enemy_groupid))])
            checkpoint.kill()

    def update(self, surface, keys):

        self.current_time = pygame.time.get_ticks()
        self.player.update(keys)

        if self.player.dead:
            if self.current_time - self.player.death_timer > 3000:
                self.finished = True
                self.update_game_info()

        elif self.is_frozen():
            pass

        else:
            self.update_player_position()
            self.check_checkpoint()
            self.check_if_go_die()
            self.update_game_window()
            self.info.update()
            self.brick_group.update()
            self.box_group.update()
            self.enemy_group.update(self)
            self.die_group.update(self)
            self.shell_group.update(self)
            self.powerup_group.update(self)
            self.coin_group.update()

        self.draw(surface)

    def is_frozen(self):
        return self.player.state in ['get_bigger', 'get_smaller', 'get_fire', 'lose_fire']


    def update_player_position(self):
        # x坐标碰撞检测
        self.player.rect.x += self.player.x_vel
        if self.player.rect.x < self.game_window.x:
            self.player.rect.x = self.game_window.x
        elif self.player.rect.right > self.end_x:
            self.player.rect.right = self.end_x
        self.check_x_collision()

        # y坐标碰撞检测
        if not self.player.dead:
            self.player.rect.y += self.player.y_vel
            self.check_y_collision()


    # x坐标碰撞检测
    def check_x_collision(self):
        items = pygame.sprite.Group(self.brick_group, self.ground_items_group, self.box_group)
        ground_item = pygame.sprite.spritecollideany(self.player, items)
        if ground_item:
            self.adjust_player_x(ground_item)

        if self.player.hurt_immune:
            return

        # 敌人的碰撞检测
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)
        if enemy:
            if self.player.big:
                self.player.state = 'get_smaller'
                self.player.hurt_immune = True
            else:
                self.player.go_die()

        # 龟壳的碰撞检测
        shell = pygame.sprite.spritecollideany(self.player, self.shell_group)
        if shell:
            if shell.state == 'slide':
                self.player.go_die()
            if self.player.rect.x < shell.rect.x:
                shell.x_vel = 10
                shell.rect.x += 40
                shell.direction = 1
            else:
                shell.x_vel = -10
                shell.rect.x -= 40
                shell.direction = 0
            shell.state = 'slide'

        # 状态道具的碰撞检测
        powerup = pygame.sprite.spritecollideany(self.player, self.powerup_group)
        if powerup:
            powerup.kill()
            if powerup.name == 'mushroom':
                self.player.state = 'get_bigger'


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
        brick = pygame.sprite.spritecollideany(self.player, self.brick_group)
        box = pygame.sprite.spritecollideany(self.player, self.box_group)
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)
        # 当砖块和宝箱同时被顶起时检测那个离马里奥更近并无视另一个
        if brick and box:
            to_brick = abs(self.player.rect.centerx - brick.rect.centerx)
            to_box = abs(self.player.rect.centerx - box.rect.centerx)
            if to_brick > to_box:
                brick = None
            else:
                box = None
        if ground_item:
            self.adjust_player_y(ground_item)
        elif brick:
            self.adjust_player_y(brick)
        elif box:
            self.adjust_player_y(box)
        elif enemy:
            if self.player.hurt_immune:
                return
            self.enemy_group.remove(enemy)
            if enemy.name == 'koopa':
                self.shell_group.add(enemy)
            else:
                self.die_group.add(enemy)

            if self.player.y_vel < 0:
                die = 'bumped'
            else:
                die = 'trampled'
                self.player.state = 'jump'
                self.player.rect.bottom = enemy.rect.top
                self.player.y_vel = self.player.jump_vel * 0.8
            enemy.go_die(die, 1 if self.player.face_right else -1)

        self.check_fall(self.player)        # 掉落检测



    def adjust_player_y(self, item):


        if self.player.rect.bottom < item.rect.bottom:
            self.player.rect.bottom = item.rect.top
            self.player.y_vel = 0
            self.player.state = 'fall'
            self.player.state = 'walk'
        else:
            self.player.y_vel = 8
            self.player.rect.top = item.rect.bottom
            self.player.state = 'fall'
            self.is_enemy_on(item)

            if item.name == 'box':
                if item.state == 'normal':
                    item.go_bumped()
            elif item.name == 'brick':
                if self.player.big and item.brick_type == 0:
                    item.smashed(self.die_group)
                else:
                    item.go_bumped()

    def is_enemy_on(self, item):
        item.rect.y -= 1
        enemy = pygame.sprite.spritecollideany(item, self.enemy_group)
        if enemy:
            self.enemy_group.remove(enemy)
            self.die_group.add(enemy)
            if item.rect.centerx > enemy.rect.centerx:
                enemy.go_die('bumped', -1)
            else:
                enemy.go_die('bumped', 1)
        item.rect.y += 1


    def check_fall(self, item):
        item.rect.y += 1
        items = pygame.sprite.Group(self.brick_group, self.ground_items_group, self.box_group)
        collided = pygame.sprite.spritecollideany(item, items)
        if not collided and item.state != 'jump' and not self.is_frozen():
            item.state= 'fall'

        item.rect.y -= 1


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
        self.coin_group.draw(self.game_ground)
        self.powerup_group.draw(self.game_ground)
        self.brick_group.draw(self.game_ground)
        self.box_group.draw(self.game_ground)
        self.enemy_group.draw(self.game_ground)
        self.die_group.draw(self.game_ground)
        self.shell_group.draw(self.game_ground)
        surface.blit(self.game_ground, (0, 0), self.game_window)
        self.info.draw(surface)
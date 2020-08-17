import pygame
from ..components import info

class LoadScreen:
    def start(self, game_info):
        self.game_info = game_info
        self.finished = False
        self.next = 'level'
        self.time_duration = 2000
        self.timer = 0
        self.info = info.Info('load_screen', self.game_info)

    def update(self, surface, keys):
        self.draw(surface)
        if self.timer == 0:
            self.timer = pygame.time.get_ticks()
        elif pygame.time.get_ticks() - self.timer > 2000:
            self.finished = True
            self.timer = 0

    def draw(self, surface):
        surface.fill((0, 0, 0))     # 黑色
        self.info.draw(surface)

class GameOver(LoadScreen):
    def start(self, game_info):
        self.game_info = game_info
        self.finished = False
        self.next = 'main_menu'
        self.time_duration = 4000
        self.timer = 0
        self.info = info.Info('game_over', self.game_info)
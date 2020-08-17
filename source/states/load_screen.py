import pygame
from ..components import info

class LoadScreen:
    def __init__(self):
        self.finished = False
        self.next = 'level'
        self.time_duration = 2000
        self.timer = 0
        self.info = info.Info('load_screen')

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
    def __init__(self):
        LoadScreen.__init__(self)
        self.next = 'main_menu'
        self.time_duration = 4000
        self.info = info.Info('game_over')
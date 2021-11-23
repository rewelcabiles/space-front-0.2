from constants import *
import pygame as pg

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = WIDTH
        self.height = HEIGHT
        self.following = None

    def follow(self, entity):
        self.following = entity

    def screen_to_world(self, x, y):
        return pg.math.Vector2((x + self.x, y + self.y))

    def update(self):
        if self.following != None:
            self.x = self.following.body.position.x - self.width / 2
            self.y = self.following.body.position.y - self.height / 2

    def render(self, screen, group):
        self.width = screen.get_rect().width 
        self.height = screen.get_rect().height
        for sprite in group:
            screen.blit(sprite.image, (
                sprite.rect.x - self.x,
                sprite.rect.y  - self.y)
                )
    
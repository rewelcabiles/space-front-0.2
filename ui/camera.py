from game.constants import *
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

    def in_camera_frame(self, point):
        if point[0]  > self.x - 200 and point[0] < self.x + self.width + 200:
            if point[1] > self.y - 200 and point[1] < self.y + self.height + 200:
                return True
        return False

    def resize(self, w, h):
        self.width = w
        self.height = h

    def render(self, screen, group):
        
        for sprite in group:
            #if self.in_camera_frame((sprite.rect.x, sprite.rect.y)):
            screen.blit(sprite.image, (
                sprite.rect.x - self.x,
                sprite.rect.y  - self.y)
                )
    
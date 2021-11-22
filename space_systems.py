from helper_functions import lerp, lerp_angle
from constants import *
from entities import Rock, Player, KineticShip
import pymunk as pm
from collision import collision_type
import pygame as pg
import math
import random

class Systems:
    def __init__(self, scene):
        self.scene = scene
        # GROUPS
        self.all_sprites = pg.sprite.Group()
        self.debris = pg.sprite.Group()
        self.faces_cursor_group = pg.sprite.Group()

        # PLAYER SETUP
        self.player = Player(scene)
        self.player.ship = KineticShip(
            [(0,50), (25,40), (50,50), (25, 0)],
            5,
            100,
            collision_type["ship"],
            RED
        )
        self.player.ship.parent = self.player
        self.scene.camera.follow(self.player.ship)
        self.scene.space.add(self.player.ship.body, self.player.ship.shape)
        self.all_sprites.add(self.player.ship)

        for r in range(16):
            new_block = Rock()
            new_block.shape.body.position = (random.randrange(WIDTH * 2), random.randrange(HEIGHT * 2))
            self.scene.space.add(new_block.body, new_block.shape)
            self.all_sprites.add(new_block)
            self.debris.add(new_block)

    def update(self, dt):
        self.all_sprites.update()
        self.player.update()



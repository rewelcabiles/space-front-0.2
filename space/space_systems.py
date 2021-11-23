from helper_functions import lerp, lerp_angle
from constants import *
from space.entities import Rock, Player, KineticShip
import pymunk as pm
from space.collision import collision_type
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
            RED,
            scene
        )
        self.player.ship.parent = self.player
        self.scene.camera.follow(self.player.ship)
        self.add_entity(self.player.ship)

        for r in range(16):
            new_block = Rock(scene)
            new_block.shape.body.position = (random.randrange(WIDTH * 2), random.randrange(HEIGHT * 2))
            self.add_entity(new_block)

    def add_entity(self, entity):
        self.all_sprites.add(entity)

    def remove_entity(self, entity):
        self.scene.space.remove(entity.body, entity.shape)
        entity.kill()

    def update(self, dt):
        self.all_sprites.update()
        self.player.update()



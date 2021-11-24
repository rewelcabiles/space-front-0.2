from game.helper_functions import MessageBoard
from game.constants import *
from space.entities import Rock, Player, KineticShip, EntityLoader
from space.collision import collision_type
import pygame as pg
import random

class Systems:
    def __init__(self, scene):
        self.scene = scene
        
        self.message_board = MessageBoard()
        self.message_board.register(self.notified)

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
            new_block = Rock()
            new_block.shape.body.position = (random.randrange(WIDTH * 2), random.randrange(HEIGHT * 2))
            self.add_entity(new_block)


    def notified(self, message):
        print(message)
        if message["subject"] == "add_entity":
            self.add_entity(message["entity"])

    def add_entity(self, entity):
        entity.systems_message_board = self.message_board
        self.scene.space.add(*entity.to_add_space)
        self.all_sprites.add(entity)

    def remove_entity(self, entity):
        self.scene.space.remove(*entity.to_add_space)
        entity.kill()

    def update(self, delta):
        self.all_sprites.update(delta)
        self.player.update(delta)



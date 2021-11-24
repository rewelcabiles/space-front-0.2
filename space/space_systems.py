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

        self.entity_dict = {}
        self.id_iter = 0
        self.reclaimable_id = []

        # GROUPS
        self.all_sprites = pg.sprite.Group()
        self.debris = pg.sprite.Group()
        self.faces_cursor_group = pg.sprite.Group()

        # PLAYER SETUP
        self.player = Player(scene)
        self.player.ship = EntityLoader.load_ship("Nem-1")
        self.player.ship.parent = self.player
        self.scene.camera.follow(self.player.ship)
        self.add_entity(self.player.ship)

        for r in range(16):
            new_block = Rock()
            new_block.shape.body.position = (random.randrange(WIDTH * 2), random.randrange(HEIGHT * 2))
            self.add_entity(new_block)


    def notified(self, message):
        if message["subject"] == "add_entity":
            self.add_entity(message["entity"])
        elif message["subject"] == "remove_entity":
            self.remove_entity(message["entity"], message["perm"])

    def new_entity_id(self):
        if self.reclaimable_id:
            return self.reclaimable_id.pop(0)
        else:
            self.id_iter += 1
            return self.id_iter

    def add_entity(self, entity):
        entity.systems_message_board = self.message_board
        entity.entity_id = self.new_entity_id()
        self.scene.space.add(*entity.to_add_space)
        self.all_sprites.add(entity)

    def remove_entity(self, entity, perm=False):
        self.scene.space.remove(*entity.to_add_space)
        entity.kill()
        if perm:
            self.reclaimable_id.append(entity.entity_id)
            del entity
        
        

    def update(self, delta):
        self.all_sprites.update(delta)
        self.player.update(delta)



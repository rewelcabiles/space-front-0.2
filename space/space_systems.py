from functools import cache
from typing import Set
from pymunk import body
from game.helper_functions import MessageBoard
from game.constants import *
from space.collision import Collision
from space.entities import DynamicBody, Rock, Player, KineticShip, EntityLoader
from space.npc import AI
import pygame as pg
import pymunk as pm
import random

class Systems:
    def __init__(self, scene):
        self.scene = scene
        
        self.space = pm.Space()
        self.space.gravity = (0, 0)
        self.space.damping = 0.9

        self.message_board = MessageBoard()
        self.message_board.register(self.notified)

        self.nav_mesh = NavMesh(self.space)

        self.entity_dict = {}
        self.id_iter = 0
        self.reclaimable_id = []
        self.ai = []

        # GROUPS
        self.all_sprites = pg.sprite.Group()
        self.debris = pg.sprite.Group()
        self.faces_cursor_group = pg.sprite.Group()

        # PLAYER SETUP
        self.player = Player(scene)
        self.player.ship = EntityLoader.load_ship("Nem-1")
        self.player.ship.body.position = (100, 100)
        self.player.ship.parent = self.player
        self.scene.camera.follow(self.player.ship)
        
        self.ai.append(self.player)
        self.add_entity(self.player.ship)

        # Random enemy
        new_npc = AI(EntityLoader.load_ship("Nem-1"))
        new_npc.ship.body.position = (35, 64)
        self.ai.append(new_npc)
        self.add_entity(new_npc.ship)
        for r in range(16):
            new_block = Rock()
            new_block.shape.body.position = (random.randrange(200, WIDTH * 2), random.randrange(HEIGHT * 2))
            self.add_entity(new_block)

        self.space.add(*[square.body for square in self.nav_mesh.squares.values()])
        self.space.add(*[square.shape for square in self.nav_mesh.squares.values()])

    def notified(self, message):
        subject = message["subject"]
        if subject == "add_entity":
            self.add_entity(message["entity"])
        elif subject == "remove_entity":
            self.remove_entity(message["entity"], message["perm"])
        elif subject == "request_coordinates":
            path = self.nav_mesh.a_star(message["start"], message["end"])
            message["callback"](path)

    def new_entity_id(self):
        if self.reclaimable_id:
            return self.reclaimable_id.pop(0)
        else:
            self.id_iter += 1
            return self.id_iter

    def add_entity(self, entity):
        entity.systems_message_board = self.message_board
        entity.entity_id = self.new_entity_id()
        self.space.add(*entity.to_add_space)
        self.all_sprites.add(entity)

    def remove_entity(self, entity, perm=False):
        self.space.remove(*entity.to_add_space)
        entity.kill()
        if perm:
            self.reclaimable_id.append(entity.entity_id)
            del entity
        
        

    def update(self, delta):
        self.space.step(delta)
        self.all_sprites.update(delta)
        for a in self.ai:
            a.update(delta)
        


class NavMesh:
    def __init__(self, space) -> None:
        self.space = space
        self.x = 0
        self.y = 0
        self.square_size = 40
        self.size_x = 43
        self.size_y = 31
        self.points = []   
        self.squares = {
            (x, y) : NavSquare(x, y, self.square_size) for x in range(self.size_x) for y in range(self.size_y)
        }
        self.occupied = {}
        #self.squares = [NavSquare(x, y, self.square_size) for x in range(self.size_x) for y in range(self.size_y)]
        #start = time.perf_counter()
        #self.a_star((0, 0), (42, 124))
        #print(time.perf_counter() - start)
        
    def dynamic_nav(self, object:DynamicBody):
        rx = object.body.position.x
        ry = object.body.position.y
        rh = object.rect.height
        rw = object.rect.width

        os1 = (int(rx / self.square_size), int(ry / self.square_size))
        os2 = (int((rx + rw) / self.square_size), int((ry + rh) / self.square_size))
        

    def point_to_square(self, point):
        pass

    
    def a_star(self, start, end):
        
        start = self.squares[(int(start[0] / self.square_size), int(start[1] / self.square_size))]
        end = self.squares[(int(end[0] / self.square_size), int(end[1] / self.square_size))]
        
        open = set()
        close = set()
        data = {k:{"in_sorted":False, "f":0, "h":0, "g": 0, "node":k, "parent":None}  for k in self.squares.values() }
        open.add(start)
        while len(open) > 0:
            current_node = sorted(open, key=lambda item: data[item]["f"])[0]
            if current_node == end:
                paz = []
                current = current_node
                while current:
                    x, y = current.get_pos()
                    paz.append((
                        (x * self.square_size) + (self.square_size / 2),
                        (y * self.square_size) + (self.square_size / 2)
                        ))
                    current = data[current]["parent"]                
                paz = paz[::-1]
                return paz

            for x_offset, y_offset in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                try:
                    neighbor = self.squares[(x_offset + current_node.x, y_offset + current_node.y)]
                except KeyError:
                    continue

                if neighbor.occupied_by > 0:
                    continue

                if not neighbor in open and not neighbor in close:
                    open.add(neighbor)
                    data[neighbor]["parent"] = current_node
                    data[neighbor]["g"] = data[current_node]["g"] + 1
                else:
                    if data[neighbor]["g"] > data[current_node]["g"] + 1:
                        data[neighbor]["g"] = data[current_node]["g"] + 1
                        data[neighbor]["parent"] = current_node
                        if neighbor in close:
                            close.remove(neighbor)
                            open.add(neighbor)

            open.remove(current_node)
            close.add(current_node)
                

        
                
class NavSquare:
    def __init__(self, x, y, size) -> None:
        self.f = 0
        self.x = x
        self.y = y
        self.body = pm.Body(body_type=pm.Body.STATIC)
        self.occupied_by = 0
        self.shape = pm.Poly(
            self.body,
             [(0,0),(size,0),(size,size),(0,size)])

        self.shape.parent = self
        self.shape.sensor = True
        self.shape.collision_type = Collision.NAV_MESH
        self.body.position = (self.x * size, self.y * size)

    def get_pos(self):
        return (self.x, self.y)
        

    
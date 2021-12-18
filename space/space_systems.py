from functools import cache
from typing import Set
from pymunk import body
from game.helper_functions import MessageBoard, Timer
from game.constants import *
from game.player import Player
from space.collision import Collision
from space.entities import DynamicBody, Rock, KineticShip, EntityLoader, SpaceStation
from space.npc import AI
import pygame as pg
import pymunk as pm
import random

from ui.ship_menu import StationMenu
#from space.scene import SpaceScene
class Systems:
    def __init__(self, scene):
        self.scene = scene
        
        self.space = pm.Space()
        self.space.gravity = (0, 0)
        self.space.damping = 0.9

        self.z_list = {}

        self.message_board = MessageBoard()
        self.message_board.register(self.notified)

        self.entity_dict = {}
        self.id_iter = 0
        self.reclaimable_id = []
        self.to_render = []
        self.ai = []

        # GROUPS
        self.all_sprites = pg.sprite.Group()
        self.nav_mesh = NavMesh(self.space, self.all_sprites)
        # PLAYER SETUP
        self.player = Player(scene)
        self.player.ship = EntityLoader.load_ship("Nem-1")
        self.player.ship.name = "PLAYER"
        print(self.player.ship)
        new_mod = EntityLoader.load_module("Projectile Cannon Mk1")
        new_mod.name = "PLAYER MOD"
        self.player.ship.comp_modules.install_module(
            new_mod
        )
        
        self.player.ship.body.position = (100, 100)
        self.player.ship.parent = self.player
        self.scene.camera.follow(self.player.ship)
        self.to_render += self.player.ship.to_render
        self.ai.append(self.player)
        self.add_entity(self.player.ship)

        # Random enemy
        new_npc = AI(EntityLoader.load_ship("Nem-1"))
        new_npc.ship.name = "AI"
        new_npc.ship.body.position = (35, 64)
        print(new_npc.ship.name)
        new_mod = EntityLoader.load_module("Projectile Cannon Mk1")
        new_mod.name = "AI MOD"
        new_npc.ship.comp_modules.install_module(new_mod)
        self.ai.append(new_npc)
        self.add_entity(new_npc.ship)
        for r in range(16):
            new_block = Rock()
            new_block.shape.body.position = (random.randrange(200, WIDTH * 2), random.randrange(HEIGHT * 2))
            self.add_entity(new_block)
        
        station_1 = SpaceStation()
        station_1.body.position = (600, 600)
        self.add_entity(station_1)



    def notified(self, message):
        subject = message["subject"]
        if subject == "add_entity":
            self.add_entity(message["entity"])
        elif subject == "remove_entity":
            self.remove_entity(message["entity"], message["perm"])
        elif subject == "request_coordinates":
            path = self.nav_mesh.a_star(message["start"], message["end"])
            message["callback"](path)
        elif subject == "space_station_accessed":
            station_id = message["station_id"]
            station_menu = StationMenu(self.scene.ui_manager,self.player)
            self.scene.dialog.goto_id("1950d26c-5cb6-414c-84d3-6fda48f842d4")



    def new_entity_id(self):
        if self.reclaimable_id:
            return self.reclaimable_id.pop(0)
        else:
            self.id_iter += 1
            return self.id_iter

    def add_entity(self, entity):
        entity.systems_message_board = self.message_board
        entity.entity_id = self.new_entity_id()
        z_index = entity.z_index
        if not z_index in self.z_list.keys():
            self.z_list[z_index] = CameraGroup(self.scene.camera)
            
        self.z_list[z_index].add(entity)
        self.space.add(*entity.to_add_space)
        self.all_sprites.add(entity)

    def remove_entity(self, entity, perm=False):
        self.space.remove(*entity.to_add_space)
        entity.kill()
        if perm:
            self.reclaimable_id.append(entity.entity_id)
            del entity
    
    def render(self, screen):

        

        sorted_z_list = sorted(self.z_list.keys())
        for k in sorted_z_list:
            v = self.z_list[k]
            v.draw(screen)

    def update(self, delta):
        self.space.step(delta)
        self.all_sprites.update(delta)
        self.nav_mesh.update(delta)
        for a in self.ai:
            a.update(delta)


class CameraGroup(pg.sprite.Group):
    def __init__(self, camera) -> None:
        super().__init__()
        self.camera = camera
    
    def draw(self, surface):
        for sprite in self.sprites():
            surface.blit(sprite.image, (
                sprite.rect.x - self.camera.x,
                sprite.rect.y  - self.camera.y)
                )










import time
import math
class NavMesh:
    IGNORED_OBJECTS =[Collision.SENSOR, Collision.SHIP, Collision.PROJECTILE, Collision.LOOT]
    def __init__(self, space, all_sprites) -> None:
        self.all_sprites = all_sprites
        self.space = space

        self.square_size = 24

        self.nav_mesh_update_timer = Timer(0.5)
        self.nav_mesh_update_timer.repeat = True
        self.nav_mesh_update_timer.call_back = self.update_nav
        self.nav_mesh_update_timer.start()

        self.total_occupied = set()
        self.total_care = set()
        self.update_nav()



    def update(self, delta):
        self.nav_mesh_update_timer.update(delta)

    def update_nav(self):
        self.total_occupied = set()
        self.total_care = set()
        for object in self.all_sprites:
            if not object.shape.collision_type in NavMesh.IGNORED_OBJECTS:
                rh = object.true_width
                rw = object.true_height
                rx = object.body.position.x 
                ry = object.body.position.y

                os1 = (int((rx - (rw / 2)) / self.square_size), int((ry - (rh / 2)) / self.square_size))
                os2 = (int((rx + rw) / self.square_size), int((ry + rh) / self.square_size))
                
                as1 = (os1[0] - 2, os1[1] - 2)
                as2 = (os2[0] + 2, os2[1] + 2)

                self.total_occupied = set.union(self.total_occupied, set((x, y) for x in range(os1[0], os2[0]) for y in range(os1[1], os2[1])))
                self.total_care = set.union(self.total_care, set((x, y) for x in range(as1[0], as2[0]) for y in range(as1[1], as2[1])))

    def heur(self, a, b):
        x_distance = abs(a[0] - b[0])
        y_distance = abs(a[1] - b[1])
        return math.sqrt( x_distance * x_distance + y_distance*y_distance)

    def a_star(self, start, end):
        timer_start = time.perf_counter()
        start = (int(start[0] / self.square_size), int(start[1] / self.square_size))
        end = (int(end[0] / self.square_size), int(end[1] / self.square_size))
        
        open = set()
        close = set()
        data = {start:{"f":0, "h":0, "g": 0, "node":start, "parent":None}}
        open.add(start)
        while len(open) > 0:

            current_node = sorted(open, key=lambda item: data[item]["f"])[0]
            if current_node == end:
                paz = []
                current = current_node
                
                old_x = current[0]
                old_y = current[1]
                old_dir = None
                while current:
                    x = current[0]
                    y = current[1]
                    direction = (x - old_x, y - old_y)
                    if old_dir == direction:
                        old_x = x
                        old_y = y
                        old_dir = direction
                        current = data[current]["parent"]
                        continue
                    old_dir = direction

                    paz.append((
                        (x * self.square_size) - (self.square_size / 2),
                        (y * self.square_size) - (self.square_size / 2)
                        ))
                    current = data[current]["parent"]                
                    old_x = x
                    old_y = y
                paz = paz[::-1]
                print(time.perf_counter() - timer_start)
                return paz

            for x_offset, y_offset in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]: # , (-1, -1), (-1, 1), (1, -1), (1, 1)
                try:
                    neighbor = (x_offset + current_node[0], y_offset + current_node[1])
                except KeyError:
                    continue
                
                if not neighbor in data.keys():
                    data[neighbor] = {"f":0, "h":0, "g": 0, "node":neighbor, "parent":None}

                if not neighbor in open and not neighbor in close:
                    open.add(neighbor)
                    data[neighbor]["parent"] = current_node
                    if neighbor in self.total_care:
                        data[neighbor]["g"] = data[current_node]["g"] + 3
                    elif neighbor in self.total_occupied:
                        data[neighbor]["g"] = data[current_node]["g"] + 999999
                    else:
                        data[neighbor]["g"] = data[current_node]["g"] + 0
                    data[neighbor]["h"] = self.heur(neighbor, end)
                    data[neighbor]["f"] = data[neighbor]["g"] + data[neighbor]["h"]

                else:
                    if data[neighbor]["g"] > data[current_node]["g"] + 1:
                        if neighbor in self.total_care:
                            data[neighbor]["g"] = data[current_node]["g"] + 3
                        elif neighbor in self.total_occupied:
                            data[neighbor]["g"] = data[current_node]["g"] + 999999
                        else:
                            data[neighbor]["g"] = data[current_node]["g"] + 0
                        data[neighbor]["h"] = self.heur(neighbor, end)
                        data[neighbor]["f"] = data[neighbor]["g"] + data[neighbor]["h"]
                        data[neighbor]["parent"] = current_node
                        if neighbor in close:
                            close.remove(neighbor)
                            open.add(neighbor)

            open.remove(current_node)
            close.add(current_node)
                

        

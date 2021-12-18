from abc import abstractmethod
from typing import List, Tuple
from game.constants import *
from pymunk import Vec2d
from game.helper_functions import Timer, lerp, lerp_angle, clamp, MessageBoard
import pygame as pg
import pymunk as pm
from space import components
import math
import random
import json

from space.collision import Collision
from space.particles import Particle, ParticleSource
import os
from glob import glob

from ui.ship_menu import StationMenu

class EntityLoader:
    images = {}
    image_path = "data/images/"
    for image in glob("data/images/*.png"):
        filename = image.split("/")[-1]
        img = pg.image.load(image).convert_alpha()
        ix, iy = img.get_size()
        img = pg.transform.scale(img, (ix * 1, iy * 1))
        images[filename] = img
    with open("data/ships.json") as f:
        ship_data = json.load(f)

    with open("data/items.json") as f:
        item_data = json.load(f)

    with open("data/modules.json") as f:
        module_data = json.load(f)

    def load_module(name):
        if name in EntityLoader.module_data.keys():
            data = EntityLoader.module_data[name].copy()
            new_module = components.Module(data)
            
            return new_module

    def load_items(name):
        if name in EntityLoader.item_data.keys():
            data = EntityLoader.item_data[name]
            new_item = Item(name, EntityLoader.images[data["image"]])
            for k, v in data.items():
                new_item.__setattr__(k, v)
            return new_item
        else:
            return ValueError

    def load_ship(name):
        if name in EntityLoader.ship_data.keys():
            data = EntityLoader.ship_data[name]

            new_ship = KineticShip(data["mass"], data["moment"], image= EntityLoader.images[data["image"]])
            new_ship.max_velocity = data["max_speed"]
            new_ship.acceleration = data["acceleration"]
            new_ship.turn_speed = data["turn_speed"] / 200
            return new_ship
        else:
            raise ValueError
    



class DynamicBody(pg.sprite.Sprite):
    def __init__(self, mass: float, moment: float, coll_type: int, body_type = pm.Body.DYNAMIC, image = EntityLoader.images["nem-1.png"]):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        self.body = pm.Body(mass, moment, body_type = body_type)
        self.shape = pm.Circle(self.body, max(self.rect.width / 2, self.rect.height / 2))
        #self.shape, self.image, self.body = create_poly_sprite( pm.Body(mass, moment, body_type = body_type), points)
        self.shape.collision_type = coll_type
        self.shape.parent = self
        self.z_index = 1
        #pg.draw.polygon(surface=self.image, color=color, points=points)
        self.set_image(self.image)
        self.max_velocity = 160
        self.parent = None
        self.message_board:MessageBoard = MessageBoard()
        self.comp_drop_table = components.DropTable(self)
        self.comp_health = components.HealthSystems(self)
        self.message_board.register(self.notified)
        self.entity_id = None
        self.systems_message_board:MessageBoard = None
        self.to_add_space = [self.shape, self.body]
        self.to_render = []
        self.timers = []
        self.true_width = self.rect.width
        self.true_height = self.rect.height

    def notified(self, message):
        if message["subject"] == "died":
            drops = self.comp_drop_table.create_drops()
            for d in drops: 
                nx, ny = self.body.position
                d.body.position = (random.randint(-30, 30) + nx, random.randint(-20, 20) + ny)
                d.body.apply_impulse_at_local_point((random.randint(-9, 9), random.randint(-9, 9)), (0, 0))
                self.systems_message_board.add_to_queue({
                    "subject" : "add_entity",
                    "entity" : d
                })
            self.destroy()
        

    def set_image(self, image):
        self.image = image
        self.orig_image = self.image
        self.rect = self.image.get_rect()

    def update(self, delta):
        for t in self.timers:
            t.update(delta)
        self.rect.center = self.body.position
        self.image = pg.transform.rotozoom( self.orig_image, math.degrees(-self.body.angle), 1)
        self.rect = self.image.get_rect(center=self.rect.center)
        # Max Velocity
        vel_x, vel_y = self.body.velocity
        vel_x = clamp(vel_x, -self.max_velocity, self.max_velocity)
        vel_y = clamp(vel_y, -self.max_velocity, self.max_velocity)
        self.body.velocity = (vel_x, vel_y)


    def destroy(self):
        self.systems_message_board.add_to_queue({
                "subject" : "remove_entity",
                "entity" : self,
                "perm" : True
            })



class KineticShip(DynamicBody):
    def __init__(self, mass: float, moment: float, image):
        DynamicBody.__init__(self, mass, moment, coll_type = Collision.SHIP, image = image)
        self.name = None
        self.acceleration = 4
        self.turn_speed = 0.08    
        self.can_interact = False
        self.interactable = None
        self.comp_cargo = components.Cargo(self)
        self.comp_modules = components.ModuleController(self)
        #self.engine_particles = ParticleSource(self)
        self.interact_sensor = pm.Circle(self.body, max(self.rect.size) + 4)
        self.interact_sensor.collision_type = Collision.SENSOR
        self.interact_sensor.parent = self
        self.interact_sensor.sensor = True
        self.to_add_space.append(self.interact_sensor)
        self.to_render = []
        self.space_breaks = False
        self.action_map = {
            "accel_forward" :False,
            "accel_backward" :False,
            "accel_left" :False,
            "accel_right" :False,
            "module_1" :False,
            "module_2" :False,
            "module_3" :False,
            "module_4" :False,
            "module_5" :False,
            "module_6" :False,
            "break" :False
        }
        # Components

    def update(self, delta):
        super().update(delta)
        x, y = self.body.velocity
        if self.action_map["accel_forward"]:
            y -= self.acceleration
        if self.action_map["accel_backward"]:
            y += self.acceleration
        if self.action_map["accel_left"]:
            x -= self.acceleration
        if self.action_map["accel_right"]:
            x += self.acceleration

        self.body.velocity = (x, y)
        if self.action_map["break"] :
            self.body.angular_velocity = lerp(self.body.angular_velocity, 0, 0.9 * delta)
            ## Air Breaks
            #x, y = self.body.velocity
            new_x = lerp(x, 0, 2 * delta)
            new_y = lerp(y, 0, 2 * delta)
            self.body.velocity = (new_x, new_y)

        self.comp_modules.update(delta)

    def face_towards(self, face_point):
        mX, mY = face_point
        goal_angle = -math.atan2(self.body.position.y - mY, mX - self.body.position.x)
        if self.body.angle != goal_angle:
            self.body.angle = lerp_angle(self.body.angle, goal_angle, self.turn_speed) # Add deltaaa


class Projectile(DynamicBody):
    def __init__(self, parent, damage, speed):
        DynamicBody.__init__(self, 0.5, 2, coll_type=Collision.PROJECTILE, image=EntityLoader.images["projectile.png"])
        self.max_velocity = speed
        self.damage = damage
        self.parent = parent
        self.death_timer = Timer(3)
        self.death_timer.call_back = self.destroy
        self.death_timer.start()
        self.timers.append(self.death_timer)

    



class Rock (DynamicBody):
    def __init__(self):
        self.size = random.randrange(30, 70)
        DynamicBody.__init__(self, self.size * 1.2, 5, coll_type=Collision.DEBRIS, image=EntityLoader.images["rock.png"])
        self.body.velocity = (random.randint(-100, 100), random.randint(-100, 100))
        self.body.angular_velocity = random.randint(-0, 5)
        self.comp_drop_table.add_to_drop_table("Rocks", 100, 6)
        self.comp_drop_table.add_to_drop_table("Ochre", 40, 10)
        self.comp_health.current_health = 50
        self.comp_health.health_capacity = 50


class Item(DynamicBody):
    def __init__(self, name, image):
        coll_type = Collision.LOOT
        self.name = name
        self.stackable = True
        self.amount = 1
        super().__init__(9, 90, coll_type=coll_type, image=image)
        self.body.velocity = (random.randint(-25, 25), random.randint(-25, 25))
        self.body.angular_velocity = random.randint(-5, 5)
        self.death_timer = Timer(60)
        self.death_timer.call_back = self.destroy
        self.timers.append(self.death_timer)
        
    def add_to_inventory(self, inventory):
        self.systems_message_board.add_to_queue({
            "subject" : "remove_entity",
            "entity" : self,
            "perm" : False
        })
        inventory.add_to_cargo(self)


class SpaceStation(DynamicBody):
    def __init__(self):
        img  = EntityLoader.images["station_1.png"]
        super().__init__(9999, 9999, coll_type=Collision.SPACE_STRUCTURE, body_type=pm.Body.DYNAMIC, image=img)
        self.body.angular_velocity = 0.1
        self.shape.sensor = True
        self.z_index = -1
        self.station_id = None

    def update(self, delta):
        super().update(delta)
        self.body.angular_velocity = 0.09

    def interact(self):
        self.systems_message_board.add_to_queue({
            "subject" : "space_station_accessed",
            "station_id" : self.station_id
        })
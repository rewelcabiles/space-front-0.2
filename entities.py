from typing import List, Tuple
from constants import *
from pymunk import Vec2d
from helper_functions import create_poly_sprite, linspace, lerp_angle, clamp
from message_board import MessageBoard
from collision import collision_type
import pygame as pg
import pymunk as pm
import components
import math
import random


class Player:
    def __init__(self, scene):
        self.message_board = MessageBoard()
        self.scene = scene
        self.ship = None

    def input(self, events):
        pass

    def update(self):
        xx, yy = pg.mouse.get_pos()
        mX, mY = self.scene.camera.screen_to_world(xx , yy)
        self.ship.face_towards((mX, mY))


class DynamicBody(pg.sprite.Sprite):
    def __init__(self, points, mass: float, moment: float, coll_type: int, color: Tuple):
        pg.sprite.Sprite.__init__(self)
        self.shape, self.image, self.body = create_poly_sprite( pm.Body(mass, moment, body_type = pm.Body.DYNAMIC), points)
        self.shape.collision_type = coll_type
        self.shape.parent = self
        pg.draw.polygon(surface=self.image, color=color, points=points)
        self.set_image(self.image)
        self.max_velocity = 68
        self.parent = None
        self.message_board:MessageBoard = MessageBoard()

    def set_image(self, image):
        self.image = image
        self.orig_image = self.image
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.center = self.body.position
        self.image = pg.transform.rotozoom( self.orig_image, math.degrees(-self.body.angle), 1)
        self.rect = self.image.get_rect(center=self.rect.center)
        vel_x, vel_y = self.body.velocity
        vel_x = clamp(vel_x, -self.max_velocity, self.max_velocity)
        vel_y = clamp(vel_y, -self.max_velocity, self.max_velocity)
        self.body.velocity = (vel_x, vel_y)


class KineticShip(DynamicBody):
    def __init__(self, points, mass: float, moment: float, coll_type: int, color: Tuple):
        DynamicBody.__init__(self, points, mass, moment, coll_type, color)
        # Components
        self.comp_health = components.HealthSystems(self.message_board)
        self.message_board.register(self.comp_health.notified)


    def face_towards(self, face_point):
        mX, mY = face_point
        goal_angle = -math.atan2(self.body.position.y - mY, mX - self.body.position.x) + math.radians(90)
        if self.body.angle != goal_angle:
            self.body.angle = lerp_angle(self.body.angle, goal_angle, 0.5)

    def spawn_projectile(self):
        projectile = Projectile()
        projectile.parent = self
        projectile.body.position = self.body.position
        projectile.body.angle = self.body.angle
        
        speed_x = 120 * math.cos(self.body.angle - math.radians(90))
        speed_y = 120 * math.sin(self.body.angle - math.radians(90))

        projectile.body.apply_impulse_at_local_point((0, -155), (0, 0))
        projectile.vel_x = speed_x
        projectile.vel_y = speed_y
        return projectile
    

class Projectile(DynamicBody):
    def __init__(self):
        points = [(0, 8), (4, 0), (8, 8), (4, 16)]
        DynamicBody.__init__(self, points, 0.5, 2, collision_type["projectile"], WHITE)
        self.max_velocity = 200



class Rock (DynamicBody):
    def __init__(self):
        self.size = random.randrange(30, 70)
        points = self.generate_points(self.size, 6, random.randrange(6, 15))
        DynamicBody.__init__(self, points, self.size * 1.2, 5000, collision_type["debris"], GREEN)
        self.comp_health = components.HealthSystems(self.message_board)
        self.message_board.register(self.comp_health.notified)

    def generate_points(self, mean_radius, sigma_radius, num_points):
        points = []
        for theta in linspace(0, 2*math.pi - (2*math.pi/num_points), num_points):
            radius = random.gauss(mean_radius, sigma_radius)
            x = mean_radius + 20 + radius * math.cos(theta)
            y = mean_radius + 20 + radius * math.sin(theta)
            points.append([x,y])
        return points





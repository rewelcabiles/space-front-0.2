from constants import *
from pymunk import Vec2d
from helper_functions import create_poly_sprite
import pygame as pg
import pymunk as pm
import math
import random


class KineticShip(pg.sprite.Sprite):
    def __init__(self, scene, space):
        pg.sprite.Sprite.__init__(self)
        # Boilerplate
        points = [(0,50), (25,40), (50,50), (25, 0)]
        self.shape, self.image, self.body = create_poly_sprite(
            pm.Body(1, 150, body_type = pm.Body.KINEMATIC),
            points,
            space
            )
        self.body.position = (150, 150)
        pg.draw.polygon(surface=self.image, color=RED, points=points)
        self.orig_image = self.image
        self.rect = self.image.get_rect()

        # Others
        self.vel_x = 0
        self.vel_y = 0
        self.max_velocity = 64
        self.scene = scene
        

class Rock (pg.sprite.Sprite):
    def __init__(self, space):
        pg.sprite.Sprite.__init__(self)

        # Pygame
        points = self.generate_points(random.randrange(30, 70), 6, random.randrange(6, 15))
        self.shape, self.image, self.body = create_poly_sprite(
            pm.Body(1, 150, body_type = pm.Body.DYNAMIC),
            points,
            space
            )
        pg.draw.polygon(surface=self.image, color=GREEN, points=points)
        self.orig_image = self.image
        self.rect = self.image.get_rect()

    def generate_points(self, mean_radius, sigma_radius, num_points):
        points = []
        for theta in linspace(0, 2*math.pi - (2*math.pi/num_points), num_points):
            radius = random.gauss(mean_radius, sigma_radius)
            x = mean_radius + 20 + radius * math.cos(theta)
            y = mean_radius + 20 + radius * math.sin(theta)
            points.append([x,y])
        print(points)
        return points


def linspace(start, stop, num_steps):
    values = []
    delta = (stop - start) / num_steps
    for i in range(num_steps):
        values.append(start + i * delta)
    return values



from helper_functions import lerp, lerp_angle
import pymunk as pm
import pygame as pg
import math

class Systems:
    def __init__(self):
        self.dynamic_bodies_group = pg.sprite.Group()
        self.kinematic_bodies_group = pg.sprite.Group()

    def dynamic_body_simulation(self):
        for bodies in self.dynamic_bodies_group:
            vel_x, vel_y = bodies.shape.body.velocity
            bodies.rect.center = bodies.body.position
            bodies.image = pg.transform.rotozoom( bodies.orig_image, math.degrees(-bodies.body.angle), 1)
            bodies.rect = bodies.image.get_rect(center=bodies.rect.center)

    def air_friction(self, cur_x, cur_y):
        air_friction = 0.1
        if cur_x > 0:
            cur_x -= air_friction
            if cur_x < 0:
                cur_x = 0
        elif cur_x < 0:
            cur_x += air_friction
            if cur_x > 0:
                cur_x = 0
        if cur_y > 0:
            cur_y -= air_friction
            if cur_y < 0:
                cur_y = 0
        elif cur_y < 0:
            cur_y += air_friction
            if cur_y > 0:
                cur_y = 0

        return cur_x, cur_y

    def kinematic_body_simulation(self):
        for bodies in self.kinematic_bodies_group:
            bodies.rect.center = bodies.body.position
            bodies.image = pg.transform.rotozoom(bodies.orig_image, math.degrees(-bodies.body.angle), 1)
            bodies.rect = bodies.image.get_rect(center=bodies.rect.center)

            xx, yy = pg.mouse.get_pos()
            mX, mY = bodies.scene.camera.screen_to_world(xx , yy)
            goal_angle = -math.atan2(bodies.body.position.y - mY, mX - bodies.body.position.x) + math.radians(90)
            if bodies.body.angle != goal_angle:
                bodies.body.angle = lerp_angle(bodies.body.angle, goal_angle, 0.08)

            bodies.vel_x, bodies.vel_y = self.air_friction(bodies.vel_x, bodies.vel_y)
            if bodies.vel_x > bodies.max_velocity:
                bodies.vel_x = bodies.max_velocity
            elif bodies.vel_x < -bodies.max_velocity:
                bodies.vel_x = -bodies.max_velocity

            if bodies.vel_y > bodies.max_velocity:
                bodies.vel_y = bodies.max_velocity

            if bodies.vel_y < -bodies.max_velocity:
                bodies.vel_y = -bodies.max_velocity

            bodies.shape.body.velocity = (bodies.vel_x, bodies.vel_y)

from space.entities import KineticShip, Rock, Projectile
from constants import *
from camera import Camera
from space.space_systems import Systems
import pygame as pg
import pymunk as pm
import random


class SceneManager:
    def __init__(self):
        self.scene_stack = []

    def new_scene(self, new_scene):
        self.scene_stack.append(new_scene)

    def render(self):
        for scene in self.scene_stack:
            scene.render()

    def update(self, delta):
        for scene in self.scene_stack:
            scene.update(delta)
    
    def input(self, events):
        for scene in self.scene_stack:
            scene.input(events)
        
import pymunk.pygame_util
from space.collision import Collision, collision_type
from space import collision

class SpaceScene:
    def __init__(self, screen):
        self.space = pm.Space()
        self.space.gravity = (0, 0)
        self.space.damping = 0.9

        self.screen = screen
        self.camera = Camera()
        self.systems = Systems(self)
        self.collisions = Collision(self)
        self.player = self.systems.player.ship
        self.draw_options = pm.pygame_util.DrawOptions(self.screen)
        
    
    def input(self, events):
        keys = pg.key.get_pressed()
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    new_proj = self.player.spawn_projectile()
                    self.space.add(new_proj.body, new_proj.shape)
                    self.systems.all_sprites.add(new_proj)
        vel_x, vel_y = self.player.body.velocity
        if keys[pg.K_a]:
            vel_x -= 0.4
        if keys[pg.K_d]:
            vel_x += 0.4
        if keys[pg.K_w]:
            vel_y -= 0.4
        if keys[pg.K_s]:
            vel_y += 0.4
        self.player.body.velocity = (vel_x, vel_y)



    def update(self, delta):
        self.systems.update(delta)
        self.camera.update()
        self.space.step(delta)
        
        

    def render(self):
        self.screen.fill(BLACK)
        self.camera.render(self.screen, self.systems.all_sprites)
        #self.space.debug_draw(self.draw_options)
        #self.all_sprites.draw(self.screen)

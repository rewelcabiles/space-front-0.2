from entities import KineticShip, Rock
from constants import *
from camera import Camera
from space_systems import Systems
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

class SpaceScene:
    def __init__(self, screen):
        self.all_sprites = pg.sprite.Group()
        self.space = pm.Space()
        self.space.gravity = (0, 0)
        self.space.damping = 0.9
        self.screen = screen
        self.camera = Camera()
        self.player = KineticShip(self, self.space)
        self.systems = Systems()
        self.camera.follow(self.player)
        self.draw_options = pm.pygame_util.DrawOptions(self.screen)

        

        for r in range(16):
            new_block = Rock(self.space)
            new_block.shape.body.position = (random.randrange(WIDTH * 2), random.randrange(HEIGHT * 2))
            self.systems.dynamic_bodies_group.add(new_block)
            self.all_sprites.add(new_block)
        
        self.systems.kinematic_bodies_group.add(self.player)
        self.all_sprites.add(self.player)
    
    def input(self, events):
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.player.vel_x -= 0.4
        if keys[pg.K_d]:
            self.player.vel_x += 0.4
        if keys[pg.K_w]:
            self.player.vel_y -= 0.4
        if keys[pg.K_s]:
            self.player.vel_y += 0.4



    def update(self, delta):
        self.systems.dynamic_body_simulation()
        self.systems.kinematic_body_simulation()
        self.camera.update()
        self.space.step(delta)
        

    def render(self):
        self.screen.fill(BLACK)
        self.camera.render(self.screen, self.all_sprites)
        
        #self.space.debug_draw(self.draw_options)
        #self.all_sprites.draw(self.screen)

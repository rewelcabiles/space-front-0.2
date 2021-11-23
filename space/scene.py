from pymunk import pygame_util
import pygame as pg
from pygame.locals import *
import pymunk as pm
from space.collision import Collision
from space.components import ModuleController
from space.entities import KineticShip
from space.space_systems import Systems
from constants import *
from ui.camera import Camera
from ui.hud import HUD


class SpaceScene:
    def __init__(self, screen):
        self.space = pm.Space()
        self.space.gravity = (0, 0)
        self.space.damping = 0.9

        self.screen = screen
        self.camera = Camera()
        self.systems = Systems(self)
        self.collisions = Collision(self)
        self.player:KineticShip = self.systems.player.ship
        self.draw_options = pm.pygame_util.DrawOptions(self.screen)

        self.hud = HUD(self.systems.player)

    def input(self, events):
        keys = pg.key.get_pressed()
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.player.comp_modules.primary_firing = True

            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.player.comp_modules.primary_firing = False

            elif event.type == VIDEORESIZE:
                self.hud.resize(event.w, event.h)

            self.hud.ui_manager.process_events(event)
        vel_x, vel_y = self.player.body.velocity
        if keys[pg.K_a]:
            vel_x -= 0.8
        if keys[pg.K_d]:
            vel_x += 0.8
        if keys[pg.K_w]:
            vel_y -= 0.8
        if keys[pg.K_s]:
            vel_y += 0.8
        self.player.body.velocity = (vel_x, vel_y)
    

    def update(self, delta):
        self.systems.update(delta)
        self.camera.update()
        self.hud.ui_manager.update(delta)
        self.space.step(delta)
        
        

    def render(self):
        self.screen.fill(BLACK)
        if DEBUG:
            self.space.debug_draw(self.draw_options)
        
        self.camera.render(self.screen, self.systems.all_sprites)
        self.hud.ui_manager.draw_ui(self.screen)

import pygame_gui
from pymunk import pygame_util
import pygame as pg
from pygame.locals import *
import pymunk as pm
from space.collision import Collision
from space.components import ModuleController
from space.entities import KineticShip
from space.space_systems import Systems
from game.constants import *
from ui.camera import Camera
from ui.hud import HUD
from ui.ship_menu import ShipMenu
import time

class SpaceScene:
    def __init__(self, screen):
        self.screen :pg.Surface = screen
        self.camera = Camera()
        self.systems = Systems(self)
        self.collisions = Collision(self)
        self.player:KineticShip = self.systems.player.ship
        self.draw_options = pm.pygame_util.DrawOptions(self.screen)
        self.font = pg.font.SysFont("Arial", 18)

        self.ui_manager =  pygame_gui.UIManager((WIDTH, HEIGHT), "ui/data/base_theme.json")
        self.hud = HUD(self.ui_manager, self.systems.player)
        self.ship_menu = ShipMenu(self.ui_manager, self.player)

    def input(self, events):
        
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.player.comp_modules.primary_firing = True

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.player.comp_modules.primary_firing = False

            if event.type == VIDEORESIZE:
                self.ui_manager.set_window_resolution((event.w, event.h))
                self.hud.resize(event.w, event.h)
                self.ship_menu.resize(event.w, event.h)

            if event.type == KEYDOWN:
                if event.key == pg.K_TAB:
                    self.ship_menu.toggle_visible()


            

            self.hud.ui_manager.process_events(event)
        if self.ship_menu.visible:
            return 
        # Space keys
        vel_x, vel_y = self.player.body.velocity
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            vel_x -= self.player.acceleration
        if keys[pg.K_d]:
            vel_x += self.player.acceleration
        if keys[pg.K_w]:
            vel_y -= self.player.acceleration
        if keys[pg.K_s]:
            vel_y += self.player.acceleration
        if keys[pg.K_z]:
            self.systems.ai[1].request_path(self.player.body.position.x, self.player.body.position.y)
            

        self.player.body.velocity = (vel_x, vel_y)
    

    def update(self, delta):
        self.systems.update(delta)
        self.camera.update()
        self.hud.ui_manager.update(delta)
        
        
        

    def render(self):
        self.screen.fill(BLACK)
        p_coords = str((int(self.player.body.position.x), int(self.player.body.position.y)))
        asd = self.font.render(p_coords, 1, WHITE)
        self.screen.blit(asd, (200,0))
        if DEBUG:
            self.systems.space.debug_draw(self.draw_options)
        if NAV_DEBUG:
            for s in self.systems.nav_mesh.squares.values():
                if s.occupied_by == 0:
                    continue
                img = pg.Surface(
                    (self.systems.nav_mesh.square_size,
                    self.systems.nav_mesh.square_size)
                    )
                img.fill(RED)
                self.screen.blit(img, (
                    s.x * self.systems.nav_mesh.square_size - self.camera.x,
                    s.y * self.systems.nav_mesh.square_size - self.camera.y))

        self.camera.render(self.screen, self.systems.all_sprites)
        self.hud.ui_manager.draw_ui(self.screen)

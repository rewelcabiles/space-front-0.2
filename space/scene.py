import pygame_gui
from pymunk import pygame_util
import pygame as pg
from pygame.locals import *
import pymunk as pm
from game.asset_loader import AssetLoader
from space.collision import Collision
from space.components import ModuleController
from space.entities import KineticShip
from space.space_systems import Systems
from game.constants import *
from ui.camera import Camera
from ui.ship_menu import Map, ShipMenu, HeadsUpDisplay
from ui.dialog import DialogTree

class SpaceScene:
    def __init__(self, screen):
        self.screen :pg.Surface = screen
        self.camera = Camera()
        self.systems = Systems(self)
        self.collisions = Collision(self)
        self.player:KineticShip = self.systems.player
        self.menu_list = []
        img = pg.Surface(
            (self.systems.nav_mesh.square_size,
            self.systems.nav_mesh.square_size)
            ).convert()
        img.fill(RED)

        self.loader :AssetLoader = AssetLoader()
        self.loader.preload_image(img, None, "debug_square")
        self.draw_options = pm.pygame_util.DrawOptions(self.screen)
        self.font = pg.font.SysFont("Arial", 18)

        self.ui_manager =  pygame_gui.UIManager((WIDTH, HEIGHT), "ui/data/base_theme.json")
        
        self.hud = HeadsUpDisplay(self.ui_manager, self.systems.player)
        self.ship_menu = ShipMenu(self.ui_manager, self.player.ship)
        self.dialog = DialogTree(self.ui_manager, self.systems)
        self.map = Map(self.player.ship, self.systems.all_sprites)



    def input(self, events):
        
        for event in events:
            self.player.do_input(event)
            if event.type == pg.USEREVENT:
                if event.user_type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
                    self.dialog.goto_id(event.link_target)

            elif event.type == VIDEORESIZE:
                self.ui_manager.set_window_resolution((event.w, event.h))
                self.hud.resize(event.w, event.h)
                self.ship_menu.resize(event.w, event.h)
                self.camera.resize(event.w, event.h)

            elif event.type == KEYDOWN:
                if event.key == pg.K_TAB:
                    self.ship_menu.toggle_visible()
                elif event.key == pg.K_z:
                    self.systems.ai[1].request_path(self.player.ship.body.position.x, self.player.ship.body.position.y)
                elif event.key == pg.K_p:
                    self.ui_manager.set_visual_debug_mode(not self.ui_manager.visual_debug_active)

            

            self.hud.ui_manager.process_events(event)

    

    def update(self, delta):
        self.systems.update(delta)
        self.camera.update()
        self.hud.ui_manager.update(delta)
        
        

    def render(self):
        self.screen.fill((5, 5, 5))
        p_coords = str((int(self.player.ship.body.position.x), int(self.player.ship.body.position.y)))
        asd = self.font.render(p_coords, 1, WHITE)
        self.screen.blit(asd, (200,0))
        
        for renderable in self.systems.to_render:
            renderable.render(self.screen, (self.camera.x, self.camera.y))
        if DEBUG:
            self.systems.space.debug_draw(self.draw_options)
        if NAV_DEBUG:
            for x , y in self.systems.nav_mesh.total_occupied:
                #if self.camera.in_camera_frame((x * self.systems.nav_mesh.square_size, y * self.systems.nav_mesh.square_size)):
                self.screen.blit(self.loader.get("debug_square")[0], (
                    x * self.systems.nav_mesh.square_size - self.camera.x,
                    y * self.systems.nav_mesh.square_size - self.camera.y))

            for points in self.systems.ai[1].move_point_queue:
                self.screen.blit(self.loader.get("debug_square")[0], (
                    points[0]  - self.camera.x,
                    points[1]  - self.camera.y))
        self.systems.render(self.screen)
        self.map.render(self.screen)
        #self.camera.render(self.screen, self.systems.all_sprites)
        self.hud.ui_manager.draw_ui(self.screen)

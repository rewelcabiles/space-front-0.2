from typing import Container
from pygame.surface import Surface
import pygame_gui
import pygame as pg
from game.constants import *
from ui.ui_manager import *


class ResizableMenu:
    def __init__(self, ui_manager, player) -> None:
        self.ui_manager = ui_manager
        self.player = player
        self.w = WIDTH
        self.h = HEIGHT
        self.resizable_rect = {}

    
from game.helper_functions import clamp    

'''
Station Actions
---------------
Main Actions ->
Hangar: Personal Ships / Buy new ships
Mechanic: Module Store
Explore: Random events
Job board: Generic jobs

Other:
For quests spawned from job boards or explore


'''

class StationMenu:
    def __init__(self, ui_manager, player) -> None:
        self.w = WIDTH
        self.h = HEIGHT
        self.player = player
        self.ui_manager = ui_manager
        self.root_panel = pygame_gui.elements.UIWindow(
            manager=self.ui_manager,
            rect=pg.Rect(0, 0, min(720, self.w), min(480, self.h)),
            window_display_title="Space Station 1"
        )
        self.hangar_button = pygame_gui.elements.UIButton( relative_rect=pg.Rect(0, 0, 100, 50),
            text="Hangar", manager=self.ui_manager, object_id="hangar_button", container=self.root_panel
        )
        self.mechanic_button = pygame_gui.elements.UIButton( relative_rect=pg.Rect(0, 120, 100, 50),
            text="Mechanic", manager=self.ui_manager, object_id="mechanic_button", container=self.root_panel
        )
        self.job_board = pygame_gui.elements.UIButton( relative_rect=pg.Rect(0, 240, 100, 50),
            text="Job Board", manager=self.ui_manager, object_id="job_board", container=self.root_panel
        )

        
        self.station_id = None

    



class Map:
    def __init__(self, player, all_sprites) -> None:
        self.w = WIDTH
        self.h = HEIGHT
        self.size_x = 200
        self.size_y = 140
        self.minimap = pg.Surface((self.size_x, self.size_y)).convert_alpha()
        self.player = player
        self.scale = 0.1
        self.all_sprites = all_sprites
        self.legends = {
            "any" : pg.Surface((4, 4)).convert()
        }

    def render(self, screen:Surface):
        self.w, self.h = screen.get_size()
        for s in self.all_sprites:
            legend = self.legends["any"]

            if s == self.player:
                legend.fill(WHITE)
            elif s.__class__.__name__ == "Rock":
                legend.fill(GREEN)
            else:
                legend.fill(BLACK)

            x = (s.rect.x * self.scale) - (self.scale * self.player.body.position.x) + (self.size_x / 2)
            y = (s.rect.y * self.scale) - (self.scale * self.player.body.position.y) + (self.size_y / 2)
            self.minimap.blit(legend,(x , y))
        
        screen.blit(self.minimap, (self.w - self.size_x, 0))
        self.minimap.fill((100, 100, 100, 50))


class HeadsUpDisplay:
    def __init__(self, ui_manager, player) -> None:
        self.w = WIDTH
        self.h = HEIGHT
        self.player = player
        self.ui_manager =  ui_manager
        self.player.ship.message_board.register(self.notified_ship)

        x, y = anchor_offset(TOP_LEFT, WIDTH, HEIGHT)


        self.hp_bar = pygame_gui.elements.UIScreenSpaceHealthBar(
            object_id="health_bar",
            relative_rect = pg.Rect(x + 10, y + 20, 240, 16),
            manager = self.ui_manager,
            sprite_to_monitor = self.player.ship.comp_health
        )
        

    def notified_ship(self, message):
        if message["subject"] == "pick_up":
            pass

    def resize(self, w, h):
        return
        x, y = anchor_offset(TOP_LEFT, w, h)
        self.hp_bar.relative_rect = pg.Rect(x + 10, y + 20, 240, 16)
        
    

class ShipMenu:
    def __init__(self, ui_manager, player) -> None:
        self.active = False
        self.visible = False    
        self.w = WIDTH
        self.h = HEIGHT
        self.margin = 20

        self.player = player
        self.ui_manager =  ui_manager

        # Root
        self.ship_menu_panel = pygame_gui.elements.UIPanel(starting_layer_height=1,
            manager=self.ui_manager,
            relative_rect=pg.Rect(self.margin, self.margin, self.w - self.margin * 2, self.h - self.margin * 2),
            visible=0,
            margins = {"top":20, "left": 20, "bottom": 20, "right": 20}
        )
        # Root -> Left
        self.left_panel = pygame_gui.elements.UIPanel(starting_layer_height=2,
            manager=self.ui_manager, relative_rect=pg.Rect(0, 0, self.w / 2, self.ship_menu_panel.relative_rect.height - 40),
            container=self.ship_menu_panel
            )
        
        # Root -> Left -> Textbox (End)
        self.cargo_label = pygame_gui.elements.UILabel( text = "Cargo Hold and Modules",
            relative_rect=pg.Rect(0, 0, self.left_panel.relative_rect.width - 10, 24),
            manager=self.ui_manager, container=self.left_panel
            )
        # Root -> Left -> Cargohold List (End)
        self.cargo_hold_container = pygame_gui.elements.UISelectionList (
            relative_rect=pg.Rect(
                0, 26,
                self.left_panel.relative_rect.width - 10,
                int(self.left_panel.relative_rect.height * 0.6)
                ),
            container=self.left_panel, manager=self.ui_manager,
            item_list=self.player.comp_cargo.get_item_list()
            )

        self.module_container = pygame_gui.elements.UIPanel (
            starting_layer_height=5,
            relative_rect=pg.Rect(
                0, -int(self.left_panel.relative_rect.height * 0.35),
                self.left_panel.relative_rect.width - 10,
                int(self.left_panel.relative_rect.height * 0.4)
                ),
            container=self.left_panel, manager=self.ui_manager,
            anchors = { "top" : "bottom", "left" : "left", "right" : "right", "bottom" : "bottom"}
            )

        

        # Root -> Right
        self.right_panel = pygame_gui.elements.UIPanel(starting_layer_height=3,
            manager=self.ui_manager,
            relative_rect=pg.Rect(
                (self.ship_menu_panel.relative_rect.width / 2) + 20 , 0,
                (self.w / 2) - 40, self.ship_menu_panel.relative_rect.height - 40),
            container=self.ship_menu_panel
            )

        
    
    def toggle_visible(self):
        self.visible = not self.visible
        if self.visible:
            self.ship_menu_panel.show()
            self.cargo_hold_container.set_item_list(self.player.comp_cargo.get_item_list())
        else:
            self.ship_menu_panel.hide()
        

    def render(self, screen):
        if not self.visible:
            return None

    def resize(self, w, h):
        self.w = w
        self.h = h
        self.ship_menu_panel.set_dimensions((self.w - self.margin * 2, self.h - self.margin * 2))
        self.left_panel.set_dimensions(((self.w / 2) - 40, self.ship_menu_panel.relative_rect.height - 40))
        

        self.right_panel.set_dimensions(((self.w / 2) - 40, self.ship_menu_panel.relative_rect.height - 40))
        self.right_panel.set_position(((self.ship_menu_panel.relative_rect.width / 2) + 20 , 40))

        self.cargo_hold_container.set_dimensions((self.left_panel.relative_rect.width - 10, int(self.left_panel.relative_rect.height * 0.6)))
        x, y = anchor_offset(TOP_RIGHT, w, h)
    
from typing import Container
import pygame_gui
import pygame as pg
from game.constants import *
from ui.ui_manager import *

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
            container=self.ship_menu_panel,
            margins = {"top":4, "left": 4, "bottom": 4, "right": 4}
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
    
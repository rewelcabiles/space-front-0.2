import pygame_gui
import pygame as pg
from game.constants import *
from space.entities import Player
from ui.ui_manager import *

class HUD:
    def __init__(self, ui_manager, player) -> None:
        self.player :Player= player
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
        x, y = anchor_offset(TOP_LEFT, w, h)
        self.hp_bar.relative_rect = pg.Rect(x + 10, y + 20, 240, 16)
        
    
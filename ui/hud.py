import pygame_gui
import pygame as pg
from constants import *
from ui.ui_manager import *
class HUD:
    def __init__(self, player) -> None:
        self.player = player
        self.ui_manager =  pygame_gui.UIManager((WIDTH, HEIGHT), "ui/data/base_theme.json")

        x, y = anchor_offset(TOP_LEFT, WIDTH, HEIGHT)
        self.hp_bar = pygame_gui.elements.UIScreenSpaceHealthBar(
            object_id="health_bar",
            relative_rect = pg.Rect(x + 10, y + 20, 240, 16),
            manager = self.ui_manager,
            sprite_to_monitor = self.player.ship.comp_health
        )
    
    def resize(self, w, h):

        x, y = anchor_offset(TOP_LEFT, w, h)
        self.hp_bar.relative_rect = pg.Rect(x + 10, y + 20, 240, 16)
        self.ui_manager.set_window_resolution((w, h))
    
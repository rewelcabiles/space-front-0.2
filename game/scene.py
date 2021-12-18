import pygame as pg
from pygame.locals import *
import pygame_gui
from pygame_gui.ui_manager import UIManager
from game.constants import *
from ui.dialog import DialogTree

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.manager  = pygame_gui.UIManager((WIDTH, HEIGHT))
        self.dialog = DialogTree(self.manager)
        
       
    def input(self, events):
        for event in events:
            if event.type == pg.USEREVENT:
                if event.user_type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
                    self.dialog.goto_id(event.link_target)
            self.manager.process_events(event)


    def update(self, delta):
        self.manager.update(delta)

        

    def render(self):
        self.screen.fill(BLACK)
        self.manager.draw_ui(self.screen)


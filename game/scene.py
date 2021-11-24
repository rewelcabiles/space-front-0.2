import pygame as pg
from pygame.locals import *
from game.constants import *
from ui.ui_manager import *

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.manager = UIManager(WIDTH, HEIGHT)
        listpanel = ListPanel(self.manager, WIDTH / 2, 20)
        
        button = UIButton(
            self.manager,
            0, 0,
            "Play"
        )

        button.anchor = MIDDLE_MIDDLE
        button2 = UIButton(
            self.manager,
            0, 200,
            "Load"
        )
        button2.anchor = MIDDLE_MIDDLE
        
       
    def input(self, events):
        pass


    def update(self, delta):
        pass

        

    def render(self):
        self.screen.fill(BLACK)
        self.manager.render(self.screen)



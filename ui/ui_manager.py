import pygame as pg
from pygame.font import SysFont
from game.constants import *

TOP_MIDDLE = 0
TOP_LEFT = 1
TOP_RIGHT = 2
MIDDLE_MIDDLE = 3
MIDDLE_LEFT = 4
MIDDLE_RIGHT = 5
BOTTOM_MIDDLE = 6
BOTTOM_LEFT = 7
BOTTOM_RIGHT = 8

class UIManager:
    def __init__(self, w, h):
        self.width = w
        self.height = h

        self.font = pg.font.SysFont('mathjax_main', 24)
        self.widget_list = []
    
    def update(self):
        pass

    def render(self, screen):
        for w in self.widget_list:
            w.render(screen)


class UIWidget:
    def __init__(self, manager:UIManager):
        self.manager = manager
        self.padding_x = 0
        self.padding_y = 0
        self.anchor = TOP_LEFT


class ListPanel(UIWidget):
    def __init__(self, manager: UIManager, x: int, y: int):
        super().__init__(manager)
        self.x = x
        self.y = y
        self.spacing = 1
        self.current_height = 0
        self.list = []

    def add(self, widget: UIWidget):
        widget.rect.x = self.x
        if len(self.list) == 0:
            widget.rect.y = self.y
            print(widget.rect.y)
        else:
            widget.rect.y = self.list[-1].rect.height + self.list[-1].rect.y + self.spacing + self.y
            print(widget.rect.y)
        self.list.append(widget)
    
class UIButton(UIWidget):
    def __init__(self, manager: UIManager, x:int, y:int, text : str, font : SysFont = None):
        super().__init__(manager)
        
        self.manager.widget_list.append(self)

        if font == None:
            self.font = self.manager.font
        else:
            self.font = font

        self.text = text
        self.text_width, self.text_height = self.font.size(self.text)
        self.padding_x = 8
        self.padding_y = 3
        self.image = pg.Surface((
            self.text_width + self.padding_x * 2,
            self.text_height + self.padding_y * 2),
            pg.SRCALPHA, 32 ).convert_alpha()
        pg.draw.rect(self.image, (255, 255, 255), (0, 0, *self.image.get_size()), border_radius=5)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.textsurface = self.font.render(self.text, False, (255, 0, 0))


    def render(self, screen):
        w, h = screen.get_size()
        anchor_x = 0
        anchor_y = 0
        if self.anchor == TOP_MIDDLE:
            anchor_x = w / 2
            anchor_y = 0
        if self.anchor == MIDDLE_MIDDLE:
            anchor_x = w / 2
            anchor_y = h / 2
        if self.anchor == BOTTOM_MIDDLE:
            anchor_x = w / 2
            anchor_y = h - self.rect.height
        if self.anchor == MIDDLE_LEFT:
            anchor_x = 0
            anchor_y = h / 2
        if self.anchor == BOTTOM_LEFT:
            anchor_x = 0
            anchor_y = h
        if self.anchor == MIDDLE_RIGHT:
            anchor_x = w
            anchor_y = h / 2
        if self.anchor == BOTTOM_RIGHT:
            anchor_x = w
            anchor_y = h
        if self.anchor == TOP_RIGHT:
            anchor_x = w - self.rect.width
            anchor_y = 0
        
        screen.blit(self.image, (
            self.rect.x - self.padding_x + anchor_x - self.rect.width / 2,
            self.rect.y - self.padding_y + anchor_y - self.rect.height / 2))
        screen.blit(self.textsurface, (
            self.rect.x + anchor_x - self.rect.width / 2,
            self.rect.y + anchor_y - self.rect.height / 2) )

def anchor_offset(anchor, w, h):
    anchor_x = 0
    anchor_y = 0
    if anchor == TOP_MIDDLE:
        anchor_x = w / 2
        anchor_y = 0
    if anchor == MIDDLE_MIDDLE:
        anchor_x = w / 2
        anchor_y = h / 2
    if anchor == BOTTOM_MIDDLE:
        anchor_x = w / 2
        anchor_y = h
    if anchor == MIDDLE_LEFT:
        anchor_x = 0
        anchor_y = h / 2
    if anchor == BOTTOM_LEFT:
        anchor_x = 0
        anchor_y = h
    if anchor == MIDDLE_RIGHT:
        anchor_x = w
        anchor_y = h / 2
    if anchor == BOTTOM_RIGHT:
        anchor_x = w
        anchor_y = h
    if anchor == TOP_RIGHT:
        anchor_x = w
        anchor_y = 0

    return anchor_x, anchor_y
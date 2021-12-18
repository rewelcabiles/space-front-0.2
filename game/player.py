import pygame as pg

from space.entities import KineticShip

class Player:
    def __init__(self, scene):
        self.scene = scene
        self.ship :KineticShip = None
        self.input_possible = True
        

    def do_input(self, event):
        if not self.input_possible:
            return
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                print(self.ship.name)
                self.ship.action_map["module_1"] = True

        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                self.ship.action_map["module_1"] = False

        elif event.type == pg.KEYDOWN:
        
            if event.key == pg.K_SPACE:
                self.ship.action_map["break"] = True
            
            elif event.key == pg.K_e:
                if self.ship.can_interact:
                    self.ship.interactable.interact()
        
            elif event.key == pg.K_a:
                self.ship.action_map["accel_left"] = True
            elif event.key == pg.K_w:
                self.ship.action_map["accel_forward"] = True
            elif event.key == pg.K_s:
                self.ship.action_map["accel_backward"] = True
            elif event.key == pg.K_d:
                self.ship.action_map["accel_right"] = True
        
        elif event.type == pg.KEYUP:
            if event.key == pg.K_SPACE:
                self.ship.action_map["break"] = False
            elif event.key == pg.K_a:
                self.ship.action_map["accel_left"] = False
            elif event.key == pg.K_w:
                self.ship.action_map["accel_forward"] = False
            elif event.key == pg.K_s:
                self.ship.action_map["accel_backward"] = False
            elif event.key == pg.K_d:
                self.ship.action_map["accel_right"] = False

        
        

    def update(self, delta):
        xx, yy = pg.mouse.get_pos()
        mX, mY = self.scene.camera.screen_to_world(xx , yy)
        self.ship.face_towards((mX, mY))
        self.ship.update(delta)

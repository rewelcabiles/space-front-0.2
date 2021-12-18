import pygame as pg
from game.helper_functions import Timer, lerp
from space.entities import KineticShip

import random
class AI:
    def __init__(self, ship:KineticShip):
        self.ship = ship
        self.move_point_queue = []
        self.face = None
        self.move_timer = Timer(5)

    def request_path_callback(self, points):
        self.move_point_queue = points
    
    def request_path(self, x, y):
        self.ship.systems_message_board.add_to_queue({
            "subject": "request_coordinates",
            "start" : (self.ship.body.position.x, self.ship.body.position.y),
            "end" : (x, y),
            "callback" : self.request_path_callback
        })

    def update(self, delta):
        self.move_timer.update(delta)
        if self.move_point_queue:
            self.ship.action_map["break"] = False
            move_target = pg.math.Vector2(self.move_point_queue[0])
            ship_pos = (self.ship.body.position.x, self.ship.body.position.y)
            vectors = (ship_pos - move_target).normalize()
            if self.face == None:
                self.ship.face_towards((move_target))
            
            to_accelerate = self.ship.acceleration * 2
            dist = move_target.distance_to(pg.math.Vector2(
                ship_pos[0] + (self.ship.rect.width / 2),
                ship_pos[1] + (self.ship.rect.height / 2)
                ))
    

            self.ship.body.velocity += (-vectors.x * to_accelerate, -vectors.y * to_accelerate)
                
            
            if  dist < max(self.ship.rect.width, self.ship.rect.height) * 10:
                self.ship.space_breaks = True
            else:
                self.ship.space_breaks = False

            if  dist < max(self.ship.rect.width, self.ship.rect.height) * 2:
                self.move_point_queue.pop(0)

        else:
            self.ship.action_map["break"] = True





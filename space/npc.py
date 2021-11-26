import pygame as pg
from pygame import draw
from pymunk import body
from game.helper_functions import Timer, lerp
from space.entities import KineticShip

import random
class AI:
    def __init__(self, ship:KineticShip):
        self.ship = ship
        #self.move_point_queue = [(210, 10), (210, 200), (0, 40), (0, 0)]
        self.move_point_queue = []
        self.face = None
        self.move_timer = Timer(5)
        self.move_timer.call_back = self.request_path
        #self.move_timer.start()

    def request_path_callback(self, points):
        print("WAHOO")
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
            
            move_target = pg.math.Vector2(self.move_point_queue[0])
            ship_pos = (self.ship.body.position.x, self.ship.body.position.y)
            
            vectors = (ship_pos - move_target).normalize()

            if self.face == None:
                self.ship.face_towards((move_target))
            
            to_accelerate = self.ship.acceleration
            dist = move_target.distance_to(pg.math.Vector2(ship_pos))
    

            self.ship.body.velocity += (-vectors.x * to_accelerate, -vectors.y * to_accelerate)
                
            
            if  dist < max(self.ship.rect.width, self.ship.rect.height) * 1.1:
                self.move_point_queue.pop(0)
                if self.move_point_queue:
                    print(f'New point!{self.move_point_queue[0]}')
                else:
                    
                    print("END OF QUEUE")
                    #self.move_timer.start()
        else:
            x, y = self.ship.body.velocity
            new_x = lerp(x, 0, 0.007)
            new_y = lerp(y, 0, 0.007)
            self.ship.body.velocity = (new_x, new_y)





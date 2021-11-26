import pygame as pg
from pygame import draw

from space.entities import KineticShip


class AI:
    def __init__(self, ship:KineticShip):
        self.ship = ship

        self.move_point_queue = [(210, 10), (210, 200), (0, 40), (0, 0)]
        self.face = None

    def update(self, delta):
        if self.move_point_queue:
            
            move_target = pg.math.Vector2(self.move_point_queue[0])
            ship_pos = (self.ship.body.position.x, self.ship.body.position.y)
            
            vectors = (ship_pos - move_target).normalize()

            if self.face == None:
                self.ship.face_towards((move_target))
            
            to_accelerate = self.ship.acceleration
            dist = move_target.distance_to(pg.math.Vector2(ship_pos))
    

            self.ship.body.velocity += (-vectors.x * to_accelerate, -vectors.y * to_accelerate)
            
            
            if  dist < max(self.ship.rect.width, self.ship.rect.height) * 2:
                self.move_point_queue.pop(0)
                if self.move_point_queue:
                    print(f'New point!{self.move_point_queue[0]}')




import pygame as pg
import random

from game.helper_functions import clamp

class Particle:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.local_x = 0
        self.local_y = 0
        self.following = 0
        self.size = 0


class ParticleSource:
    def __init__(self, following) -> None:
        self.particles = []

        self.following = following
        self.local_x = 8
        self.local_y = 8
        self.x = 0
        self.y = 0

    def render(self, screen, offset):
        self.x = self.following.body.position.x - self.local_x
        self.y = self.following.body.position.y - self.local_y
        velx, vely = self.following.body.velocity
      
        velx = clamp(velx, -4, 4) + random.randint(-2, 2)
        vely = clamp(vely, -4, 4)
        self.particles.append(
            [[self.x - offset[0], self.y - offset[1]],
            [-velx, -vely],
            random.randint(4, 9)])
        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.80
            #particle[1][1] += 0.80
            pg.draw.circle(screen, (255, 255, 255), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))
            if particle[2] <= 0:
                self.particles.remove(particle)

        
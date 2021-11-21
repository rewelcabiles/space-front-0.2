from constants import *
import pymunk as pm
import pygame as pg
import math

def lerp(a, b, t):
    return a + (b - a) * t


def shortAngleDist(a,b):
    maxs = math.pi * 2
    da = (b - a) % maxs;
    return 2 * da % maxs - da;


def lerp_angle(a, b, t):
    return a + shortAngleDist(a,b) * t

def create_poly_sprite(body, points, space):
    hx = 0
    hy = 0
    for cx, cy in points:
         hx = cx if cx > hx else hx
         hy = cy if cy > hy else hy
    offset_x = hx / 2
    offset_y = hy / 2
    pm_points = []
    for cx, cy in points:
        cx -= offset_x
        cy -= offset_y
        pm_points.append((cx, cy))
    
    shape = pm.Poly(body, pm_points)
    image = pg.Surface((hx , hy), pg.SRCALPHA, 32 ).convert_alpha()
    
    space.add(body, shape)

    return shape, image, body
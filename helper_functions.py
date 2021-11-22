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

def create_poly_sprite(body, points):
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

    return shape, image, body

def linspace(start, stop, num_steps):
    values = []
    delta = (stop - start) / num_steps
    for i in range(num_steps):
        values.append(start + i * delta)
    return values

def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)

def air_friction(cur_x, cur_y):
    air_friction = 0.1
    if cur_x > 0:
        cur_x -= air_friction
        if cur_x < 0:
            cur_x = 0
    elif cur_x < 0:
        cur_x += air_friction
        if cur_x > 0:
            cur_x = 0
    if cur_y > 0:
        cur_y -= air_friction
        if cur_y < 0:
            cur_y = 0
    elif cur_y < 0:
        cur_y += air_friction
        if cur_y > 0:
            cur_y = 0

    return cur_x, cur_y

import pygame as pg
import pymunk as pm
import math

from message_board import MessageBoard

class HealthSystems:
    def __init__(self, message_board: MessageBoard, base_hp = 100) -> None:
        self.message_board = message_board
        self.base_hp = base_hp
        self.cur_hp = base_hp

    def take_damage(self, damage: int) -> None:
        self.cur_hp -= damage
        print("OOF")
        print(damage)
        self.message_board.add_to_queue({
            "subject": "damage_received",
            "damage" : damage
        })

    def notified(self, message):
        if message["subject"] == "take_damage":
            self.take_damage(message["damage"])

    def notify(self, message):
        self.message_board.add_to_queue(message)
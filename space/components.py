import pygame as pg
import pymunk as pm
import math
import random
from helper_functions import MessageBoard

class Systems:
    def __init__(self, message_board: MessageBoard, parent) -> None:
        self.parent = parent
        self.message_board = message_board
    
    def notify(self, message):
        self.message_board.add_to_queue(message)

    

class HealthSystems(Systems):
    def __init__(self, message_board: MessageBoard, parent, base_hp = 100) -> None:
        super().__init__(message_board, parent)
        self.base_hp = base_hp
        self.health_capacity = base_hp
        self.current_health = base_hp

    def take_damage(self, damage: int) -> None:
        self.current_health -= damage
        print(self.current_health)
        self.message_board.add_to_queue({
            "subject": "damage_received",
            "damage" : damage
        })
        if self.current_health <= 0:
            print("DIED1")
            self.message_board.add_to_queue({
              "subject": "died"
            })

    def notified(self, message):
        if message["subject"] == "take_damage":
            self.take_damage(message["damage"])

    
class DropTable(Systems):
    def __init__(self, message_board: MessageBoard, parent) -> None:
        super().__init__(message_board, parent)
        self.drop_table = {} # name : {object, chance, amount}

    def add_to_drop_table(self, name, object, chance, amount):
        self.drop_table[name] = {
            "object" : object,
            "chance" : chance,
            "amount" : amount
        }

    def create_drops(self):
        to_spawn = []
        
        for v in self.drop_table.values():
            print("SUCCESS")
            if v["chance"] > random.randint(0, 100):
                print("SUCCESS1")
                for a in range(random.randint(1, v["amount"])):
                    print("woo")
                    to_spawn.append(v["object"](self.parent.scene))
        return to_spawn

        



class Inventory(Systems):
    def __init__(self, message_board: MessageBoard) -> None:
        super().__init__(message_board)
        self.maximum_weight = 100
        self.current_weight = 0
        self.cargo_hold = []

    def add_to_cargo(self, item):
        self.current_weight += item.weight
        self.cargo_hold.append(item)
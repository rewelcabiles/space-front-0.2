import pygame as pg
import pymunk as pm
import math
import random
from game.helper_functions import MessageBoard
from space.entities import Projectile, EntityLoader

class Systems:
    def __init__(self, message_board: MessageBoard, parent) -> None:
        self.parent = parent
        self.message_board = message_board
    
    def notify(self, message):
        self.message_board.add_to_queue(message)

    def notified(self, message):
        raise NotImplementedError(("This aint implemented yet"))


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
            if v["chance"] > random.randint(0, 100):
                for a in range(random.randint(1, v["amount"])):
                    to_spawn.append(v["object"](self.parent.scene))
        return to_spawn

        
class ModuleController(Systems):
    PRIMARY = 1
    SECONDARY = 2
    def __init__(self, message_board: MessageBoard, parent) -> None:
        super().__init__(message_board, parent)

        self.primary_firing = False
        self.secondary_firing = False

        self.primary_module = ProjectileWeaponModule(self)
        self.secondary_module = None

    def update(self, delta):
        if self.primary_module != None:
            if self.primary_firing:
                self.activate_module(ModuleController.PRIMARY)
            self.primary_module.update(delta)

        if self.secondary_module != None:
            if self.secondary_module:
                self.activate_module(ModuleController.SECONDARY)
            self.secondary_module.update(delta)

    def activate_module(self, module):
        if module == ModuleController.PRIMARY and self.primary_module != None:
            projectiles = self.primary_module.fire()
            if projectiles:
                for p in projectiles:
                    self.parent.systems_message_board.add_to_queue({
                        "subject" : "add_entity",
                        "entity" : p
                    })

        elif module == ModuleController.SECONDARY:
            pass
            

class Module:
    def __init__(self, module_controller:ModuleController) -> None:
        self.module_controller = module_controller

    def fire(self):
        pass

class ProjectileWeaponModule(Module):
    def __init__(self, module_controller :ModuleController) -> None:
        super().__init__(module_controller)
        self.fire_rate = 0.6
        self.fire_rate_cd = 0
        self.can_fire = True

    def update(self, delta):
        if not self.can_fire:
            self.fire_rate_cd += 1 * delta
            print(self.fire_rate_cd)
            if self.fire_rate_cd >= self.fire_rate:
                print("CAN FIRE NOW")
                self.can_fire = True

    def fire(self):
        if self.can_fire:
            self.can_fire = False
            self.fire_rate_cd = 0
            projectile = Projectile(self.module_controller.parent.scene)
            projectile.parent = self.module_controller.parent
            projectile.body.position = projectile.parent.body.position
            projectile.body.angle = projectile.parent.body.angle
            
            speed_x = 120 * math.cos(projectile.parent.body.angle - math.radians(90))
            speed_y = 120 * math.sin(projectile.parent.body.angle - math.radians(90))

            projectile.body.apply_impulse_at_local_point((0, -355), (0, 0))
            projectile.vel_x = speed_x
            projectile.vel_y = speed_y
            
            return [projectile]
        
        
            


class Cargo(Systems):
    def __init__(self, message_board: MessageBoard, parent) -> None:
        super().__init__(message_board, parent)
        self.maximum_weight = 100
        self.current_weight = 0
        self.cargo_hold = []

    def notified(self, message):
        if message["subject"] == "pick_up":
            message["data"].add_to_inventory(self)

    def add_to_cargo(self, item):
        #self.current_weight += item.weight
        self.cargo_hold.append(item)
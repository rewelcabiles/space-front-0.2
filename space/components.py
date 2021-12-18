
import math
import random
from game.helper_functions import MessageBoard, Timer
from space.entities import Projectile, EntityLoader

class Systems:
    def __init__(self, parent):
        self.parent = parent
        self.message_board = self.parent.message_board
        self.message_board.register(self.notified)
    
    def notify(self, message):
        self.message_board.add_to_queue(message)

    def notified(self, message):
        pass


class HealthSystems(Systems):
    def __init__(self, parent, base_hp = 100) -> None:
        super().__init__(parent)
        self.base_hp = base_hp
        self.health_capacity = base_hp
        self.current_health = base_hp
        self.invulnerable = False

    def take_damage(self, damage: int) -> None:
        if self.invulnerable:
            return
        self.current_health -= damage
        self.message_board.add_to_queue({
            "subject": "damage_received",
            "damage" : damage
        })
        if self.current_health <= 0:
            self.message_board.add_to_queue({
              "subject": "died"
            })

    def notified(self, message):
        if message["subject"] == "take_damage":
            self.take_damage(message["damage"])

    
class DropTable(Systems):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.drop_table = {} # name : {object, chance, amount}

    def add_to_drop_table(self, name, chance, amount):
        self.drop_table[name] = {
            "chance" : chance,
            "amount" : amount
        }

    def create_drops(self):
        to_spawn = []
        
        for k, v in self.drop_table.items():
            if v["chance"] > random.randint(0, 100):
                for a in range(random.randint(1, v["amount"])):
                    to_spawn.append(EntityLoader.load_items(k))
        return to_spawn

'''
Module System Plan:
======================
SHIP:
    Ships have a certain amount of "Module Space"
    Module space increases with Ship class
    Module space varies with ship archetype (+/- module space)
    Any amount of Modules can be installed as long as there is module space on the ship.

MODULE:
    Modules are either passive or active
    Active modules are activated via M1, M2, or 1 - 0
    Some Modules may draw power from the ship power supply


'''


            

class Module:
    def __init__(self, d):
        self.__dict__ = d
        self.name = None
        for k, v in self.type_data.items():
            setattr(self, k, v)

        self.module_controller = None
        self.module_space_requirement = 1
        self.modifies = {}
        self.passive = False

    def update(self, delta):
        if self.type == "projectile_weapon":
            if not self.can_fire:
                self.fire_rate_cd += 1 * delta
                if self.fire_rate_cd >= self.fire_rate:
                    self.can_fire = True

    def activate(self):
        if self.type == "projectile_weapon":
            self.activate_projectile_weapon()

    def activate_projectile_weapon(self):
        
        if self.can_fire:
            self.can_fire = False
            self.fire_rate_cd = 0
            print(self.module_controller.parent.name)
            projectile = Projectile(self.module_controller.parent, self.proj_damage, self.proj_speed)
            projectile.body.position = projectile.parent.body.position
            projectile.body.angle = projectile.parent.body.angle
            
            speed_x = 120 * math.cos(projectile.parent.body.angle)
            speed_y = 120 * math.sin(projectile.parent.body.angle)

            projectile.body.apply_impulse_at_local_point((355, 0), (0, 0))
            projectile.vel_x = speed_x
            projectile.vel_y = speed_y
            
            self.module_controller.parent.systems_message_board.add_to_queue({
                "subject" : "add_entity",
                "entity" : projectile
            })

class ModuleController(Systems):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.max_module_space = 10
        self.cur_module_space = 0
        self.installed_modules = []
        
        
    def install_module(self, module:Module):
        print(f'{self.parent.name=}, {module.name=}')
        if not module.module_space_requirement + self.cur_module_space > self.max_module_space:
            self.cur_module_space += module.module_space_requirement
            module.module_controller = self
            self.installed_modules.append(module)
            print(f'{self.parent.name=}, {module.name=}')
            for mod, value in module.modifies.items():
                self.message_board.add_to_queue({
                    "subject" : "modify_attribute",
                    "attribute" : mod,
                    "value" : value
                })
            

    def remove_module(self, module :Module):
        self.installed_modules.remove(module)
        module.module_controller = None
        self.cur_module_space -= module.module_space_requirement
        for mod, value in module.modifies.items():
            self.message_board.add_to_queue({
                "subject" : "modify_attribute",
                "attribute" : mod,
                "value" : -value
            })

    def notified(self, message):
        if message["subject"] == "install_module":
            self.install_module(message["module"])
        
        elif message["subject"] == "remove_module":
            self.remove_module(message["module"])

    def update(self, delta):
        for mods in self.installed_modules:
            if mods != None:
                mods.update(delta)
        
        if self.parent.action_map["module_1"] and not self.installed_modules[0] is None:
            self.installed_modules[0].activate()

        

            

class Cargo(Systems):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.maximum_weight = 100
        self.current_weight = 0
        self.cargo_hold = {}
        self.cargo_hold_names = {}

    def notified(self, message):
        if message["subject"] == "pick_up":
            message["data"].add_to_inventory(self)

    def add_to_cargo(self, item):

        if item.name not in self.cargo_hold_names:
            self.cargo_hold[item.entity_id] = item
            self.cargo_hold_names[item.name] = item

        elif item.stackable:
            self.cargo_hold_names[item.name].amount += 1

        else:
            self.cargo_hold[item.entity_id] = item


    def get_item_list(self):
        print(self.cargo_hold)
        return ["{}x   {}".format(x.amount, x.name) for x in self.cargo_hold.values()]
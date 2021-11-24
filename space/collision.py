
col_list = [
    "debris", "player", "projectile", "ship", "loot", "sensor", "interactable"
]
collision_type = dict(zip(col_list, range(len(col_list))))

class Collision:
    def __init__(self, scene):
        self.scene = scene
        self.space = self.scene.space
        self.system = self.scene.systems
        
        self.space.add_collision_handler(collision_type["ship"], collision_type["debris"]).begin = self.ship_collides
        self.space.add_collision_handler(collision_type["sensor"], collision_type["loot"]).begin = self.pick_up_item

        self.space.add_wildcard_collision_handler(collision_type["projectile"]).begin = self.projectile_hit

    def pick_up_item(self, arbiter, space, data):
        ship = arbiter.shapes[0].parent
        loot = arbiter.shapes[1].parent
        ship.message_board.add_to_queue({
            "subject" : "pick_up",
            "data" : loot
        })

        
        return True

    def ship_collides(self, arbiter, space, data):
        ship = arbiter.shapes[0].parent
        debris = arbiter.shapes[1].parent
        mass_difference = (debris.body.mass - ship.body.mass) / 100
        damage = 0
        if mass_difference < 0:
            damage = 1 + mass_difference
        else:
            damage = mass_difference

        ship.message_board.add_to_queue({
            "subject" : "take_damage",
            "damage" : abs(mass_difference * 5)
        })

        return True

    def projectile_hit(self, arbiter, space, data):
        projectile = arbiter.shapes[0].parent
        other = arbiter.shapes[1].parent

        if projectile.parent == other:
            return False

        if arbiter.is_first_contact:
            other.message_board.add_to_queue({
                "subject" : "take_damage",
                "damage" : projectile.damage
            })

            self.scene.systems.message_board.add_to_queue({
                "subject": "remove_entity",
                "entity" : projectile,
                "perm" : True
            })
        

            
        return True

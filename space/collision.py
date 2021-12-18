

class Collision:
    col_list = [
        "debris", "player", "projectile", "ship", "loot", "sensor", "interactable", 
        "background_entity", "SPACE_STRUCTURE"
    ]
    for k, v in dict(zip(col_list, range(len(col_list)))).items():
        vars()[k.upper()] = v
        
    def __init__(self, scene):
        self.scene = scene
        self.space = self.scene.systems.space
        self.system = self.scene.systems
        
        self.space.add_collision_handler(Collision.SHIP, Collision.DEBRIS).begin = self.ship_collides
        self.space.add_collision_handler(Collision.SENSOR, Collision.LOOT).begin = self.pick_up_item
        self.space.add_collision_handler(Collision.SENSOR, Collision.SPACE_STRUCTURE).begin = self.interactable
        self.space.add_collision_handler(Collision.SENSOR, Collision.SPACE_STRUCTURE).separate = self.interactable_end

        self.space.add_wildcard_collision_handler(Collision.PROJECTILE).begin = self.projectile_hit
        self.space.add_wildcard_collision_handler(Collision.SPACE_STRUCTURE).begin = self.ignore_collision


    def ignore_collision(self, arbiter, space, data):
        if arbiter.shapes[1].collision_type in [Collision.SENSOR]:
            return True    
        return False

    def interactable_end(self, arbiter, space, data):
        ship = arbiter.shapes[0].parent
        ship.can_interact = False
        ship.interactable = None
        return True

    def interactable(self, arbiter, space, data):
        ship = arbiter.shapes[0].parent
        ship.interactable = arbiter.shapes[1].parent
        ship.can_interact = True
        return True

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
        
        if arbiter.shapes[1].collision_type == Collision.BACKGROUND_ENTITY:
            return False

        mass_difference = (debris.body.mass - ship.body.mass) / 100
        message = {
            "subject" : "take_damage",
            "damage" : int(abs(mass_difference * 5))
        }
        ship.message_board.add_to_queue(message)
        debris.message_board.add_to_queue(message)

        return True

    def projectile_hit(self, arbiter, space, data):
        projectile = arbiter.shapes[0].parent
        other = arbiter.shapes[1].parent
        if projectile.parent == other:
            return False

        if arbiter.shapes[1].collision_type in [Collision.SPACE_STRUCTURE, Collision.SENSOR, Collision.PROJECTILE, Collision.BACKGROUND_ENTITY]:
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

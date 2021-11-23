

class SceneManager:
    def __init__(self):
        self.scene_stack = []

    def new_scene(self, new_scene):
        self.scene_stack.append(new_scene)

    def render(self):
        for scene in self.scene_stack:
            scene.render()

    def update(self, delta):
        for scene in self.scene_stack:
            scene.update(delta)
    
    def input(self, events):
        for scene in self.scene_stack:
            scene.input(events)


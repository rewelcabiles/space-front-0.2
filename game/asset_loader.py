




class AssetLoader:
    def __init__(self) -> None:
        self.assets = {}

    def preload_image(self, image, points, name):
        self.assets[name] = [image, points]

    def get(self, name):
        return self.assets[name]
from constants import *
from pygame.locals import *
from scenes import SceneManager, SpaceScene
import pygame as pg


class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Outer Space")
        screen = pg.display.set_mode((WIDTH, HEIGHT), RESIZABLE)
        self.clock = pg.time.Clock()
        self.game_running = True
        self.scene_manager = SceneManager()
        self.scene_manager.new_scene(SpaceScene(screen))
        
    def run(self):
        while self.game_running:
            time = self.clock.tick(FPS)
            events = pg.event.get()
            for event in events:    
                if event.type == pg.QUIT:
                    self.game_running = False
                elif event.type == VIDEORESIZE:
                    WIDTH = event.w
                    HEIGHT = event.h
                    screen = pg.display.set_mode((event.w,event.h),RESIZABLE)

            delta = 1 / float(time)
            self.scene_manager.update(delta)
            self.scene_manager.render()
            self.scene_manager.input(events)

            pg.display.flip()
        
        pg.quit()



if __name__ == '__main__':
    g = Game()
    g.run()
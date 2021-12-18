from game.constants import *
from pygame.locals import *
from game.scenes import SceneManager

#from game.scene import MainMenu
import pygame as pg


class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Outer Space")
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), RESIZABLE)
        self.clock = pg.time.Clock()
        self.game_running = True
        self.debug_mode = True
        self.scene_manager = SceneManager()
        from space.scene import SpaceScene
        self.scene_manager.new_scene(SpaceScene(self.screen))
        
    def run(self):
        font = pg.font.SysFont("Arial", 18)

        t = pg.time.get_ticks()
        getTicksLastFrame = t


        while self.game_running:
            t = pg.time.get_ticks()
            self.clock.tick()
            events = pg.event.get()
            for event in events:    
                if event.type == pg.QUIT:
                    self.game_running = False
                elif event.type == VIDEORESIZE:
                    WIDTH = event.w
                    HEIGHT = event.h
                    self.screen = pg.display.set_mode((event.w,event.h),RESIZABLE)
            
            delta = (t - getTicksLastFrame) / 1000.0
            getTicksLastFrame = t
            self.scene_manager.update(delta)
            self.scene_manager.render()
            self.scene_manager.input(events)
            if self.debug_mode:
                fps = str(int(self.clock.get_fps()))
                fps_text = font.render(fps, 1, WHITE)
                self.screen.blit(fps_text, (10,0))

                delta = str(delta)
                delta_text = font.render(delta, 1, WHITE)
                self.screen.blit(delta_text, (100,0))

            pg.display.flip()
        
        pg.quit()



if __name__ == '__main__':
    g = Game()
    g.run()
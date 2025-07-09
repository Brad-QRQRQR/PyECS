import pygame
import engine

class Game:
    # constant
    FPS: int = 60
    DEFAULT_COLOR: tuple[int, int, int] = (0, 0, 0)
    
    def __init__(self):
        # init pygame
        pygame.init()

        self.ecs = engine.framework.ECS()

        self.is_run: bool = True
        self.window: pygame.Surface = pygame.display.set_mode((300, 300))
        self.display: pygame.Surface = pygame.Surface((self.window.get_width() / 2, self.window.get_height() / 2))
        self.clock: pygame.time.Clock = pygame.time.Clock()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_run = False

    def update(self) -> None:
        pass

    def render(self) -> None:
        surf: pygame.Surface = pygame.transform.scale(self.display, (self.window.get_width(), self.window.get_height()))
        self.window.blit(surf, (0, 0))
        pygame.display.update()

    def run(self) -> None:
        while (self.is_run):
            self.window.fill(Game.DEFAULT_COLOR)
            self.update()
            self.input()
            self.render()
            self.clock.tick(Game.FPS)
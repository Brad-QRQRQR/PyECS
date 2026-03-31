import sys

from engine.framework import *
from engine.render import *
from engine.physics import *

class GameLoop:
    def __init__(
        self,
        width: int,
        height: int,
        layer: int,
        fps: int,
        *,
        flags: int = 0,
        background_color: tuple[int, int, int, int] = (255, 255, 255, 255),
        tot_coll_types: int = 0,
        chunk_size = 64
    ):
        pygame.init()
        self.window = pygame.display.set_mode((width, height), flags=flags)
        self.ecs: Ecs = Ecs()
        self.render_manager: RenderManager = RenderManager(layer, width, height, background_color=background_color)
        self.collision_sys: Collision = Collision(tot_coll_types, chunk_size)
        
        self.is_run: bool = True
        self.FPS: int = fps
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.dt: float = 0.0
        self.time_step: float = 1 / fps

        self.key_comb_to_event: dict[tuple[int, int], tuple[str, bool]] = dict()
        self.input_status: dict[str, bool] = dict()
        self.__key_event: tuple[int, int] = (
            pygame.KEYDOWN,
            pygame.KEYUP,
        )
        self.__mouse_event: tuple[int, int] = (
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP
        )
        print(background_color)

    def set_input_with_key(self, key_status: int, key: int, event: str, boolean: bool) -> None:
        self.key_comb_to_event[(key_status, key)] = (event, boolean)
        self.input_status[event] = False

    def get_input(self, event: str) -> bool:
        if event not in self.input_status:
            raise KeyError
        return self.input_status[event]

    def input(self) -> None:
        key_comb: tuple[int, int]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_run = False
                pygame.quit()
                sys.exit(0)
            for key_event in self.__key_event:
                if event.type != key_event:
                    continue
                key_comb = (key_event, event.key)
                if key_comb in self.key_comb_to_event:
                    res: tuple[str, bool] = self.key_comb_to_event[key_comb]
                    self.input_status[res[0]] = res[1]
            for mouse_event in self.__mouse_event:
                if event.type != mouse_event:
                    continue
                key_comb = (mouse_event, event.button)
                if key_comb in self.key_comb_to_event:
                    res: tuple[str, bool] = self.key_comb_to_event[key_comb]
                    self.input_status[res[0]] = res[1]

    def update(self) -> None:
        raise NotImplementedError

    def run(self) -> None:
        while self.is_run:
            while self.dt >= self.time_step:
                self.input()
                self.update()
                self.render_manager.process(self.ecs, self.window)
                self.collision_sys.clear_evnet(self.ecs)
                self.ecs.clear_buffer()
                self.ecs.remove_dead_entities()
                self.dt -= self.time_step
            self.dt += self.clock.tick(self.FPS) / 1000
            # self.dt = min(self.dt, 1)
            
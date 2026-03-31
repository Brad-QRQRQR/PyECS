from engine.framework import *

from engine.misc.gameloop import GameLoop

class OnStart:
    registry: list["OnStart"] = []
    def __init_subclass__(cls) -> None:
        cls.registry.append(cls())

    def start(self, game_loop: GameLoop) -> None:
        raise NotImplementedError

    @classmethod
    def perfrom(cls, game_loop: GameLoop) -> None:
        for func in cls.registry:
            func.start(game_loop)

    @classmethod
    def clear_registry(cls) -> None:
        cls.registry.clear()

class OnUpdate:
    registry: list["OnUpdate"] = []
    def __init_subclass__(cls) -> None:
        cls.registry.append(cls())

    def update(self, game_loop: GameLoop) -> None:
        raise NotImplementedError

    @classmethod
    def perfrom(cls, game_loop: GameLoop) -> None:
        for func in cls.registry:
            func.update(game_loop)

    @classmethod
    def clear_registry(cls) -> None:
        cls.registry.clear()

class OnCollision:
    registry: list["OnCollision"] = []
    def __init_subclass__(cls) -> None:
        cls.registry.append(cls())

    def respond(self, game_loop: GameLoop) -> None:
        raise NotImplementedError

    @classmethod
    def perfrom(cls, game_loop: GameLoop) -> None:
        for func in cls.registry:
            func.respond(game_loop)

    @classmethod
    def clear_registry(cls) -> None:
        cls.registry.clear()
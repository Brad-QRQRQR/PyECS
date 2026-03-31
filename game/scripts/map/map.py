import engine

from game.scripts.compoents.comp import CollTile

def create_boundary(game_loop: engine.GameLoop) -> None:
    # four corners
    game_loop.ecs.register_entity(
        engine.components.Collider(
            engine.components.Point(0, 0),
            engine.components.Rect(16, 16),
            engine.components.Rect(16, 16),
        ),
        engine.components.CollisionType(1),
        CollTile(),
    )
    game_loop.ecs.register_entity(
        engine.components.Collider(
            engine.components.Point(0, 320 - 16),
            engine.components.Rect(16, 16),
            engine.components.Rect(16, 16),
        ),
        engine.components.CollisionType(1),
        CollTile(),
    )
    game_loop.ecs.register_entity(
        engine.components.Collider(
            engine.components.Point(240 - 16, 0),
            engine.components.Rect(16, 16),
            engine.components.Rect(16, 16),
        ),
        engine.components.CollisionType(1),
        CollTile(),
    )
    game_loop.ecs.register_entity(
        engine.components.Collider(
            engine.components.Point(240 - 16, 320 - 16),
            engine.components.Rect(16, 16),
            engine.components.Rect(16, 16),
        ),
        engine.components.CollisionType(1),
        CollTile(),
    )

    # four walls
    game_loop.ecs.register_entity(
        engine.components.Collider(
            engine.components.Point(16, 0),
            engine.components.Rect(320 - 32, 16),
            engine.components.Rect(320 - 32, 16),
        ),
        engine.components.CollisionType(1),
        CollTile(),
    )
    game_loop.ecs.register_entity(
        engine.components.Collider(
            engine.components.Point(320 - 16, 16),
            engine.components.Rect(16, 240 - 32),
            engine.components.Rect(16, 240 - 32),
        ),
        engine.components.CollisionType(1),
        CollTile(),
    )
    game_loop.ecs.register_entity(
        engine.components.Collider(
            engine.components.Point(16, 240 - 16),
            engine.components.Rect(320 - 32, 16),
            engine.components.Rect(320 - 32, 16),
        ),
        engine.components.CollisionType(1),
        CollTile(),
    )
    game_loop.ecs.register_entity(
        engine.components.Collider(
            engine.components.Point(0, 16),
            engine.components.Rect(16, 240 - 32),
            engine.components.Rect(16, 240 - 32),
        ),
        engine.components.CollisionType(1),
        CollTile(),
    )
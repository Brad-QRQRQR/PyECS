import random
import math
import engine

from game.scripts.compoents.comp import *

class EnemyShooterStart(engine.OnStart):
    DEFAULT_SPAWN_TIME: int = 3
    DEFAULT_DAMAGE: int = 3
    def start(self, game_loop: engine.GameLoop) -> None:
        game_loop.ecs.register_entity(
            EnemySpawn(
                spawn_timer=0,
                max_spawn_time=EnemyShooterStart.DEFAULT_SPAWN_TIME,
            )
        )
    
class EnemyShooterUpdate(engine.OnUpdate):
    def update(self, game_loop: engine.GameLoop) -> None:
        self.spawner: EnemySpawn = [comps[0]() for eid, comps in game_loop.ecs.query_with_component(EnemySpawn)][0]
        self.spawner.spawn_timer -= game_loop.time_step
        if self.spawner.spawn_timer <= 0:
            x = random.randint(25, 50)
            y = random.randint(25, 50)
            game_loop.ecs.register_entity(
                engine.components.Point(
                    x,
                    y,
                ),
                engine.components.Rect(16, 16),
                engine.components.Color(50, 0, 0),
                engine.components.RenderableRect(),
                game_loop.render_manager.get_layer(2)(),
                engine.components.Renderer(engine.render.RenderId.RECT),
                engine.components.Collider(
                    engine.components.Point(x, y),
                    engine.components.Rect(16, 16),
                    engine.components.Rect(16, 16),
                ),
                engine.components.CollisionType(game_loop.collision_sys.get_tag_id(EnemyShooter)),
                EnemyShooter(),
            )
            self.spawner.spawn_timer = self.spawner.max_spawn_time
    
    def shoot(self, game_loop: engine.GameLoop) -> None:
        for eid, comps in game_loop.ecs.query_with_component(EnemyShooter):
            pass
    
class EnemyShooterOnColiision(engine.OnCollision):
    def respond(self, game_loop: engine.GameLoop) -> None:
        for eid, comps in game_loop.ecs.query_with_component(
            engine.components.CollisionEvent,
            EnemyShooter,
        ):
            coll_event: engine.components.CollisionEvent = comps[0]()

            ent_1: engine.framework.Entity = game_loop.ecs.get_entity(coll_event.e1)
            ent_2: engine.framework.Entity = game_loop.ecs.get_entity(coll_event.e2)

            pos_1: engine.components.Point = ent_1.get(engine.components.Point)
            rect_1: engine.components.Rect = ent_1.get(engine.components.Rect)
            
            pos_2: engine.components.Point = ent_2.get(engine.components.Point)
            radius_2: engine.components.Radius = ent_2.get(engine.components.Radius)

            res = engine.physics.aabb_to_circle_detect(
                pos_1,
                rect_1,
                pos_2,
                radius_2,
            )

            if res[0]:
                game_loop.ecs.mark_dead_entity(coll_event.e1)

                for _ in range(10):
                    angle = random.randint(0,360)
                    engine.effects.emit_spark(
                        game_loop.ecs,
                        engine.components.Point(
                            pos_1.x + rect_1.width / 2,
                            pos_1.y + rect_1.height / 2,
                        ),
                        engine.components.Velocity(
                            30,
                            angle
                        ),
                        engine.components.Acceleration(),
                        engine.components.Color(150, 0, 20),
                        engine.components.SparkOption(0.1, 3.5, 0.3),
                        engine.components.FadeRate(0.05),
                        game_loop.render_manager,
                        2,
                    )

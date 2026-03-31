import math
import random
import pygame
import engine

from game.scripts.compoents.comp import *

class PlayerInit(engine.OnStart):
    DEFAULT_MAX_STRENGTH: int = 300
    DEFAULT_POWER_INC: int = 2
    DEFAULT_SHOOT_TIME: float = 0.5
    DEFAULT_INVULNERALBE_TIME: float = 3

    def start(self, game_loop: engine.GameLoop) -> None:
        pid: int = game_loop.ecs.register_entity(
            engine.components.Point(80, 80),
            engine.components.Radius(16),
            engine.components.Velocity(0, 0),
            engine.components.Speed(0, 0),
            engine.components.Acceleration(),
            engine.components.Renderable(
                game_loop.render_manager.surf_pool.get_tag_id("player"),
                game_loop.render_manager.surf_pool.get_sta_id("player", "idle"),
                0,
                x_shift=-16,
                y_shift=-16,
            ),
            engine.components.Renderer(engine.render.RenderId.SURF),
            game_loop.render_manager.get_layer(1)(),
            engine.components.Collider(
                engine.components.Point(80 - 16, 80 - 16),
                engine.components.Rect(32, 32),
                engine.components.Rect(32, 32),
            ),
            engine.components.Transform(),
            engine.components.CollisionType(0),
            PlayerConfig(
                strength=0,
                power_inc=PlayerInit.DEFAULT_POWER_INC,
                max_strength=PlayerInit.DEFAULT_MAX_STRENGTH,
                friction=1,
                shoot_timer=0,
                max_shoot_time=PlayerInit.DEFAULT_SHOOT_TIME,
                invulnerable=0,
                max_invul_time=PlayerInit.DEFAULT_INVULNERALBE_TIME,
            ),
            Player(),
        )
        eid: int = game_loop.ecs.register_entity(
            engine.components.Combination(
                pid,
                -1,
                -1,
                -1,
                -1,
            ),
            PlayerShoot(),
        )
        game_loop.ecs.get_entity(eid).get(engine.components.Combination).root = eid

class PlayerUpdate(engine.OnUpdate):
    def update(self, game_loop: engine.GameLoop) -> None:
        self.entity_id: int = \
            [eid for eid, comps in game_loop.ecs.query_with_component(PlayerConfig)][0]
        self.entity = game_loop.ecs.get_entity(self.entity_id)
        
        self.power_up(game_loop.get_input("power_up"))
        self.launch_attack(game_loop.get_input("attack"), game_loop)
        self.make_invulnerable(game_loop.get_input("skill_1"), game_loop)
        self.frictionize()
        self.shoot(game_loop)

        # adjust collider lower point
        self.entity.get(engine.components.Collider).aabb_lower_p.x = \
            self.entity.get(engine.components.Point).x - self.entity.get(engine.components.Radius).r
        self.entity.get(engine.components.Collider).aabb_lower_p.y = \
            self.entity.get(engine.components.Point).y - self.entity.get(engine.components.Radius).r
    
    def power_up(self, power: bool) -> None:
        if power:
            self.entity.get(PlayerConfig).strength = min(self.entity.get(PlayerConfig).strength + self.entity.get(PlayerConfig).power_inc, self.entity.get(PlayerConfig).max_strength)
        else:
            self.entity.get(PlayerConfig).strength = max(self.entity.get(PlayerConfig).strength - self.entity.get(PlayerConfig).power_inc, 0)

    def launch_attack(self, attack: bool, game_loop: engine.GameLoop) -> None:
        if attack and self.entity.get(engine.components.Velocity).v == 0:
            self.entity.get(PlayerConfig).shoot_timer = self.entity.get(PlayerConfig).max_shoot_time
            scroll = engine.render.camera_get_scroll(game_loop.ecs)
            mpos = pygame.mouse.get_pos()
            rad = math.atan2(
                scroll[1] + mpos[1] / 2 - self.entity.get(engine.components.Point).y,
                scroll[0] + mpos[0] / 2 - self.entity.get(engine.components.Point).x,
            )
            self.entity.get(engine.components.Velocity).v = self.entity.get(PlayerConfig).strength
            self.entity.get(engine.components.Speed).dx = self.entity.get(PlayerConfig).strength * math.cos(rad)
            self.entity.get(engine.components.Speed).dy = self.entity.get(PlayerConfig).strength * math.sin(rad)
            self.entity.get(engine.components.Velocity).angle = rad * (180 / math.pi)
            self.entity.get(PlayerConfig).strength = 0
        # print(self.entity.get(engine.components.Velocity), self.entity.get(engine.components.Transform).angle)

    def frictionize(self) -> None:
        vel = self.entity.get(engine.components.Velocity).v
        vel = self.entity.get(engine.components.Velocity).v = max(0, vel - self.entity.get(PlayerConfig).friction)
        rad = math.radians(self.entity.get(engine.components.Velocity).angle)
        self.entity.get(engine.components.Speed).dx = vel * math.cos(rad)
        self.entity.get(engine.components.Speed).dy = vel * math.sin(rad)

    def add_shooter(self, ecs: engine.framework.Ecs) -> None:
        pass

    def shoot(self, game_loop: engine.GameLoop) -> None:
        pass
    
    def make_invulnerable(self, used: bool, game_loop: engine.GameLoop) -> None:
        pass

class PlayerOnCollision(engine.OnCollision):
    def respond(self, game_loop: engine.GameLoop) -> None:
        for eid, comps in game_loop.ecs.query_with_component(
            engine.components.CollisionEvent,
            CollTile,
        ):
            coll_event: engine.components.CollisionEvent = comps[0]()

            ent1: engine.framework.Entity = game_loop.ecs.get_entity(coll_event.e2)
            ent2: engine.framework.Entity = game_loop.ecs.get_entity(coll_event.e1)

            pos1 = ent1.get(engine.components.Point)
            radius1 = ent1.get(engine.components.Radius)
            speed1 = ent1.get(engine.components.Speed)
            vel1 = ent1.get(engine.components.Velocity)

            pos2 = ent2.get(engine.components.Collider).aabb_lower_p
            rect2 = ent2.get(engine.components.Collider).aabb_outer_box
            
            res = engine.physics.aabb_to_circle_detect(
                pos2,
                rect2,
                engine.components.Point(
                    pos1.x + speed1.dx * game_loop.time_step,
                    pos1.y + speed1.dy * game_loop.time_step,
                ),
                radius1,
            )
            if res[0]:
                pos1.x += res[1][0] * res[2]
                pos1.y += res[1][1] * res[2]

                vx = speed1.dx
                vy = speed1.dy

                vel1.v = max(0, vel1.v - 60)
                vx = vel1.v * math.cos(math.radians(vel1.angle))
                vy = vel1.v * math.sin(math.radians(vel1.angle))

                vx, vy = engine.geometry.vector_reflect(vx, vy, res[1])
                vel1.angle = math.atan2(vy, vx) * (180 / math.pi)

                speed1.dx = vx
                speed1.dy = vy

                for _ in range(10):
                    angle = engine.geometry.vector_angle(res[1][0], res[1][1], 0, 1) * (180 / math.pi) + random.randint(-90, 90)
                    engine.effects.emit_spark(
                        game_loop.ecs,
                        engine.components.Point(
                            pos1.x - res[1][0] * radius1.r,
                            pos1.y - res[1][1] * radius1.r,
                        ),
                        engine.components.Velocity(
                            50,
                            angle
                        ),
                        engine.components.Acceleration(),
                        engine.components.Color(200, 255, 220),
                        engine.components.SparkOption(0.15, 4, 0.35),
                        engine.components.FadeRate(0.15),
                        game_loop.render_manager,
                        2,
                    )
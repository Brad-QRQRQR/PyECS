import pygame
import engine
import random
import math
import os

from game.scripts.compoents.comp import *
from game.scripts.map.map import *
from game.scripts.player.player import *
from game.scripts.enemy.enemy import *

class Game(engine.GameLoop):
    def __init__(self):
        super().__init__(640, 360, 3, 60, tot_coll_types=3, background_color=(0, 0, 0, 255))

        self.render_manager.surf_pool.load_info_from_json("assets/image_info")
        self.render_manager.surf_pool.load_surf("assets")

        self.collision_sys.build_tag_table(
            [
                Player,
                CollTile,
                EnemyShooter,
            ]
        )
        self.collision_sys.build_mask(
            [
                0b110,
                0b001,
                0b001,
            ]
        )

        engine.gamemap.tile_map_load_from_csv(self.ecs, self.render_manager, "little", "tile")
        # engine.gamemap.tile_map_load_collider_info_from_csv(self.ecs, self.collision_sys, "coll_info")
        create_boundary(self)
        engine.render.build_camera(
            self.ecs,
            (self.render_manager.display.width // 4, self.render_manager.display.height // 4),
            (0, 0),
            2,
            (0, 640),
            (0, 360),
        )

        engine.OnStart.perfrom(self)

        self.set_input_with_key(pygame.KEYDOWN, pygame.K_SPACE, "power_up", True)
        self.set_input_with_key(pygame.KEYUP, pygame.K_SPACE, "power_up", False)
        self.set_input_with_key(pygame.MOUSEBUTTONDOWN, 1, "attack", True)
        self.set_input_with_key(pygame.MOUSEBUTTONUP, 1, "attack", False)
        self.set_input_with_key(pygame.KEYDOWN, pygame.K_1, "skill_1", True)
        self.set_input_with_key(pygame.KEYUP, pygame.K_1, "skill_1", False)
        self.set_input_with_key(pygame.KEYDOWN, pygame.K_2, "skill_2", True)
        self.set_input_with_key(pygame.KEYUP, pygame.K_2, "skill_2", False)
        self.set_input_with_key(pygame.KEYDOWN, pygame.K_3, "skill_3", True)
        self.set_input_with_key(pygame.KEYUP, pygame.K_3, "skill_3", False)

        # self.debugger = engine.debug.EngineDebuger()

    def update(self) -> None:
        # object update
        engine.effects.spark_fade(self.ecs, self.time_step)
        engine.effects.particle_fade(self.ecs, self.time_step)
        engine.action.update_combination(self, engine.components.LightingShape, engine.effects.lighting_particle_update)
        engine.OnUpdate.perfrom(self)
        
        # collision check and response
        engine.physics.adjust_collider_outer_box(self.ecs, self.time_step)
        self.collision_sys.check_collision(self.ecs)
        engine.OnCollision.perfrom(self)

        # move
        engine.physics.move_with_speed(self.ecs, self.time_step)

        # camera movement
        for eid, comps in self.ecs.query_with_component(engine.components.Point, Player):
            focus: engine.components.Point = comps[0]()
            engine.render.camera_change_foucs(self.ecs, focus.x, focus.y)
            engine.render.camera_follow(self.ecs)

        # gui update
        engine.gui.update_gui_with_scroll(self.ecs)
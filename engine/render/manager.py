import pygame

from typing import Any
from enum import IntEnum
from weakref import ReferenceType

import engine.framework as framework
import engine.components as ecomp

from engine.render.surfpool import SurfPool

class RenderId(IntEnum):
    SURF = 0
    CIRCLE = 1
    CIRCLE_LIGHTNING = 2
    RECT = 3
    POLYGON = 4
    LINE = 5

class RenderManager:
    def __init__(self, max_layer: int, width: int, height: int, background_color: tuple[int, int, int, int]):
        self.__max_layer: int = max_layer
        self.__layers: list[type[Any]] = [self._make_layer_tag(i) for i in range(0, self.__max_layer)]
        self.__background_color: tuple[int, int, int, int] = background_color
        
        self.__func: tuple[Render, ...] = (
            SurfRender(),
            CircleRender(),
            CircleLightingRender(),
            RectRender(),
            PolygonRender(),
            LineRender(),
        )
        self.__func_param: tuple[tuple[type[Any], ...], ...] = (
            (ecomp.Point, ecomp.Transform, ecomp.Renderable),
            (ecomp.Point, ecomp.Radius, ecomp.Color, ecomp.RenderableCircle),
            (ecomp.Point, ecomp.Radius, ecomp.Color, ecomp.LightingShape),
            (ecomp.Point, ecomp.Rect, ecomp.Color, ecomp.RenderableRect),
            (ecomp.PointSet, ecomp.Color, ecomp.RenderablePolygon),
            (ecomp.Segment, ecomp.Color, ecomp.RenderableSegment),
        )

        self.display: pygame.Surface = pygame.Surface((width, height)).convert()
        self.surf_pool: SurfPool = SurfPool()

    def add_layer(self) -> None:
        self.__layers.append(self._make_layer_tag(self.__max_layer))
        self.__max_layer += 1

    def get_layer(self, idx: int) -> type[Any]:
        return self.__layers[idx]
    
    def get_max_layer_idx(self) -> int:
        return self.__max_layer - 1

    def _make_layer_tag(self, idx: int) -> type[Any]:
        return type("Layer" + str(idx), (object,), {})

    def process(self, ecs: framework.Ecs, window: pygame.Surface) -> None:
        self.display.fill(self.__background_color)
        scale_size: tuple[int, int] = (self.display.get_width(), self.display.get_height())
        scroll: tuple[int, int] = (0, 0)
        for eid, comps in ecs.query_with_component(ecomp.CameraOption):
            camera: ecomp.CameraOption = comps[0]()
            scroll = (int(camera.scroll_x), int(camera.scroll_y))
            scale_size = (int(self.display.get_width() * camera.zoom_size), int(self.display.get_height() * camera.zoom_size))
        for layer in self.__layers:
            for param in self.__func_param:
                for eid, comps in ecs.query_with_component(layer, ecomp.Renderer, *param):
                    render = comps[1]()
                    self.__func[render.render_id].process(self, comps[2:], scroll)
        surf: pygame.Surface = pygame.transform.scale(self.display, scale_size)
        window.blit(surf, (0, 0))
        pygame.display.flip()

class Render:
    def process(self, manager: RenderManager, info: tuple[ReferenceType, ...], scroll: tuple[int, int]) -> None:
        raise NotImplementedError

class SurfRender(Render):    
    def process(self, manager: RenderManager, info: tuple[ReferenceType, ...], scroll: tuple[int, int]) -> None:
        pos: ecomp.Point = info[0]() # type: ignore
        renderable: ecomp.Renderable = info[2]() # type: ignore
        if not renderable.visible or not is_visible(pos, scroll, manager.display.width, manager.display.height):
            return
        
        transform: ecomp.Transform = info[1]() # type: ignore

        if transform.flip_x or transform.flip_y or transform.angle != 0 or transform.scale != 1:
            surf_copy: pygame.Surface = manager.surf_pool.get_surf((renderable.tag, renderable.sta), renderable.frame).copy()
            px: int = int(pos.x) + int(surf_copy.width / 2)
            py: int = int(pos.y) + int(surf_copy.height / 2)

            if transform.angle_gap == 0 or transform.scale_gap == 0:
                if transform.scale != 1:
                    surf_copy = pygame.transform.scale(surf_copy, (surf_copy.width * transform.scale, surf_copy.height * transform.scale))
                if transform.flip_x or transform.flip_y:
                    surf_copy = pygame.transform.flip(surf_copy, transform.flip_x, transform.flip_y)
                if transform.angle != 0:
                    surf_copy = pygame.transform.rotate(surf_copy, -1 * transform.angle)
            else:
                scale_id = int(transform.scale / transform.scale_gap)
                angle_id = int(transform.angle / transform.angle_gap)
                surf_id = (renderable.tag, renderable.sta, renderable.frame)
                trans_param = (scale_id, angle_id, transform.flip_x, transform.flip_y)
                surf_from_pool = manager.surf_pool.get_transform_surf(surf_id, trans_param)
                
                if surf_from_pool is None:
                    if transform.scale != 1:
                        surf_copy = pygame.transform.scale(surf_copy, (surf_copy.width * transform.scale, surf_copy.height * transform.scale))
                    if transform.flip_x or transform.flip_y:
                        surf_copy = pygame.transform.flip(surf_copy, transform.flip_x, transform.flip_y)
                    if transform.angle != 0:
                        surf_copy = pygame.transform.rotate(surf_copy, -1 * transform.angle)

                    manager.surf_pool.set_transform_surf(surf_id, trans_param, surf_copy)
                else:
                    surf_copy = surf_from_pool
            
            px -= int(surf_copy.width / 2)
            py -= int(surf_copy.height / 2)

            manager.display.blit(
                surf_copy,
                (int(px) + renderable.x_shift - scroll[0], int(py) + renderable.y_shift - scroll[1]),
                special_flags = renderable.flag,   
            )
        else:
            manager.display.blit(
                manager.surf_pool.get_surf((renderable.tag, renderable.sta), renderable.frame),
                (int(pos.x) + renderable.x_shift - scroll[0], int(pos.y) + renderable.y_shift - scroll[1]),
                special_flags = renderable.flag,
            )

class CircleRender(Render):
    def process(self, manager: RenderManager, info: tuple[ReferenceType, ...], scroll: tuple[int, int]) -> None:
        pos: ecomp.Point = info[0]() # type: ignore
        renderable: ecomp.RenderableCircle = info[3]() # type: ignore
        if not renderable.visible or not is_visible(pos, scroll, manager.display.width, manager.display.height):
            return
        radius: ecomp.Radius = info[1]() # type: ignore
        color: ecomp.Color = info[2]() # type: ignore
        pygame.draw.circle(
            manager.display,
            (color.r, color.g, color.b, color.alpha),
            (int(pos.x) - scroll[0], int(pos.y) - scroll[1]),
            radius.r,
            width=renderable.width
        )

class CircleLightingRender(Render):
    def process(self, manager: RenderManager, info: tuple[ReferenceType, ...], scroll: tuple[int, int]) -> None:
        pos: ecomp.Point = info[0]() # type: ignore
        radius: ecomp.Radius = info[1]() # type: ignore
        if not is_visible(pos, scroll, manager.display.width, manager.display.height) and \
        not is_visible(ecomp.Point(pos.x + radius.r, pos.y + radius.r), scroll, manager.display.width, manager.display.height) and \
        not is_visible(ecomp.Point(pos.x - radius.r, pos.y - radius.r), scroll, manager.display.width, manager.display.height) and \
        not is_visible(ecomp.Point(pos.x - radius.r, pos.y), scroll, manager.display.width, manager.display.height) and \
        not is_visible(ecomp.Point(pos.x + radius.r, pos.y), scroll, manager.display.width, manager.display.height) and \
        not is_visible(ecomp.Point(pos.x, pos.y - radius.r), scroll, manager.display.width, manager.display.height) and \
        not is_visible(ecomp.Point(pos.x, pos.y + radius.r), scroll, manager.display.width, manager.display.height):
            return
        color: ecomp.Color = info[2]() # type: ignore
        light: ecomp.LightingShape = info[3]() # type: ignore
        light_surf = pygame.Surface((radius.r * 2, radius.r * 2)).convert()
        pygame.draw.circle(light_surf, (color.r, color.g, color.b, color.alpha), (radius.r, radius.r), radius.r)
        light_surf.set_colorkey((0, 0, 0))
        manager.display.blit(light_surf, (int(pos.x) - scroll[0], int(pos.y) - scroll[1]), special_flags = light.flag)

class RectRender(Render):
    def process(self, manager: RenderManager, info: tuple[ReferenceType, ...], scroll: tuple[int, int]) -> None:
        pos: ecomp.Point = info[0]() # type: ignore
        renderable: ecomp.RenderableRect = info[3]() # type: ignore
        if not renderable.visible or not is_visible(pos, scroll, manager.display.width, manager.display.height):
            return
        rect: ecomp.Rect = info[1]() # type: ignore
        color: ecomp.Color = info[2]() # type: ignore
        pygame.draw.rect(
            manager.display,
            (color.r, color.g, color.b, color.alpha),
            (int(pos.x) - scroll[0], int(pos.y) - scroll[1], rect.width, rect.height),
            renderable.width
        )

class PolygonRender(Render):
    def process(self, manager: RenderManager, info: tuple[ReferenceType, ...], scroll: tuple[int, int]) -> None:
        pset: ecomp.PointSet = info[0]() # type: ignore
        renderable: ecomp.RenderablePolygon = info[2]() # type: ignore
        if not renderable.visible or all(not is_visible(pos, scroll, manager.display.width, manager.display.height) for pos in pset.points):
            return
        color: ecomp.Color = info[1]() # type: ignore
        pygame.draw.polygon(
            manager.display,
            (color.r, color.g, color.b, color.alpha),
            [(int(pos.x) - scroll[0], int(pos.y) - scroll[1]) for pos in pset.points],
            renderable.width,
        )

class LineRender(Render):
    def process(self, manager: RenderManager, info: tuple[ReferenceType, ...], scroll: tuple[int, int]) -> None:
        segment: ecomp.Segment = info[0]() # type: ignore
        renderable: ecomp.RenderableSegment = info[2]() # type: ignore
        if not renderable.visible:
            return
        if not is_visible(segment.start, scroll, manager.display.width, manager.display.height):
            return
        if not is_visible(segment.end, scroll, manager.display.width, manager.display.height):
            return
        color: ecomp.Color = info[1]() # type: ignore
        pygame.draw.line(
            manager.display,
            (color.r, color.g, color.b, color.alpha),
            (segment.start.x - scroll[0], segment.start.y - scroll[1]),
            (segment.end.x - scroll[0], segment.end.y - scroll[1]),
            renderable.width,
        )

def is_visible(pos: ecomp.Point, scroll: tuple[int, int], width: int, height: int, offset: int = 16) -> bool:
    cx = pos.x - scroll[0]
    cy = pos.y - scroll[1]
    if cx < -offset or cy < -offset or cx > width + offset or cy > height + offset:
        return False
    return True
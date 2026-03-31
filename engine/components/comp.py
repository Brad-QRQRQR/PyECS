from typing import Callable
from dataclasses import dataclass as component

############
# Geometry
############

@component
class Point:
    x: float
    y: float

@component
class Speed:
    dx: float = 0
    dy: float = 0

@component
class Mass:
    m: int

@component
class Force:
    fx: float = 0
    fy: float = 0

@component
class Acceleration:
    ax: float = 0
    ay: float = 0

@component
class Rect:
    width: int | float
    height: int | float

@component
class Radius:
    r: float

@component
class Velocity:
    v: float
    angle: float

@component
class PointSet:
    points: list[Point]

@component
class Segment:
    start: Point
    end: Point

############
# Collision
############

@component
class Collider:
    aabb_lower_p: Point
    aabb_outer_box: Rect
    aabb_inner_box: Rect

@component
class CollisionType:
    val: int

@component
class CollisionEvent:
    e1: int 
    e2: int

############
# AI Behaviour
############

@component
class State:
    state_id: int

############
# Rendering
############

@component
class Renderer:
    render_id: int = 0

@component
class Transform:
    angle: float = 0
    scale: float = 1
    flip_x: bool = False
    flip_y: bool = False
    angle_gap: int | float = 20
    scale_gap: int | float = 1

@component
class Renderable:
    tag: int
    sta: int
    frame: int
    flag: int = 0
    x_shift: int = 0
    y_shift: int = 0
    visible: bool = True

@component
class RenderableCircle:
    width: int = 0
    visible: bool = True

@component
class RenderableRect:
    width: int = 0
    visible: bool = True

@component
class RenderablePolygon:
    width: int = 0
    visible: bool = True

@component
class RenderableSegment:
    width: int = 0
    visible: bool = True

@component
class Color:
    r: int = 0
    g: int = 0
    b: int = 0
    alpha: int = 255

@component
class LightingShape:
    flag: int = 0

@component
class CameraOption:
    focus_x: int | float
    focus_y: int | float
    scale: int | float
    follow_factor: int | float = 5
    zoom_factor: int | float = 1
    left_border: int = 0
    top_border: int = 0
    right_border: int = 0
    bottom_border: int = 0
    zoom_size: int | float = 2
    scroll_x: int | float = 0
    scroll_y: int | float = 0

############
# Other
############

@component
class FadeRate:
    rate: float

@component
class SparkOption:
    scale: float
    tail_factor: float
    width_factor: float

@component
class Gui:
    x: int = 0
    y: int = 0

############
# Tag
############

@component
class Tile:
    pass

############
# Relation
############

@component
class Relation:
    val: int
    root: int
    parent: int
    nxt: int
    prv: int

@component
class Combination(Relation):
    rel_x: float = 0
    rel_y: float = 0
    
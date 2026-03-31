import math
import engine.components as ecomp

def sort_points_couterclockwise(pset: list[ecomp.Point]) -> None:
    cx: float = get_center_x(pset)
    cy: float = get_center_y(pset)
    pset.sort(key=lambda pt: math.atan2(pt.y - cy, pt.x - cx), reverse=True)

def get_transform_points(pset: list[ecomp.Point], transform: ecomp.Transform) -> list[ecomp.Point]:
    cx: float = get_center_x(pset)
    cy: float = get_center_y(pset)
    for pt in pset:
        pt.x -= cx
        pt.y -= cy
        if transform.angle != 0:
            pt.x, pt.y = rotate_point(pt.x, pt.y, -1 * transform.angle)
        if transform.scale != 1:
            pt.x, pt.y = scale_point(pt.x, pt.y, transform.scale)
        if transform.flip_x:
            pt.x, pt.y = flip_point_to_x(pt.x, pt.y)
        if transform.flip_y:
            pt.x, pt.y = flip_point_to_y(pt.x, pt.y)
        pt.x += cx
        pt.y += cy
        # pt.x = int(pt.x)
        # pt.y = int(pt.y)
    return pset

def rotate_point(px: int | float, py: int | float, angle: int | float) -> tuple[float, float]:
    radian = math.radians(angle)
    px, py = math.cos(radian) * px - math.sin(radian) * py, math.sin(radian) * px + math.cos(radian) * py
    return px, py

def scale_point(px: int | float, py: int | float, scale: int | float) -> tuple[float, float]:
    return px * scale, py * scale

def flip_point_to_x(px: int | float, py: int | float) -> tuple[int | float, int | float]:
    return px, -py

def flip_point_to_y(px: int | float, py: int | float) -> tuple[int | float, int | float]:
    return -px, py

def get_center_x(pset: list[ecomp.Point]) -> float:
    return sum(pt.x for pt in pset) / len(pset)

def get_center_y(pset: list[ecomp.Point]) -> float:
    return sum(pt.y for pt in pset) / len(pset)
import engine.components as ecomp

def rect_get_right(pos: ecomp.Point, rect: ecomp.Rect) -> int | float:
    return pos.x + rect.width

def rect_get_bottom(pos: ecomp.Point, rect: ecomp.Rect) -> int | float:
    return pos.y + rect.height

def rect_get_points(pos: ecomp.Point, rect: ecomp.Rect) -> list[ecomp.Point]:
    return [
        ecomp.Point(pos.x, pos.y),
        ecomp.Point(pos.x + rect.width, pos.y),
        ecomp.Point(pos.x, pos.y + rect.height),
        ecomp.Point(pos.x + rect.width, pos.y + rect.height),
    ]
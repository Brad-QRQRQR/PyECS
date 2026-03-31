import math

def get_y_online_with_x(m: int | float, x0: int | float, y0: int | float, x: int | float) -> float:
    return y0 + m * (x - x0)

def get_x_online_with_y(m: int | float, x0: int | float, y0: int | float, y: int | float) -> float:
    return (y - y0) / m + x0 if m != 0 else x0

def distance(pax: int | float, pay: int | float, pbx: int | float, pby: int | float) -> float:
    return math.sqrt((pax - pbx) * (pax - pbx) + (pay - pby) * (pay - pby))

def square_distance(pax: int | float, pay: int | float, pbx: int | float, pby: int | float) -> int | float:
    return (pax - pbx) * (pax - pbx) + (pay - pby) * (pay - pby)

def get_slope(x0: int | float, y0: int | float, x1: int | float, y1: int | float) -> float:
    return (y1 - y0) / (x1 - x0)

def get_intersection_with_two_lines(m0: int | float, x0: int | float, y0: int | float, m1: int | float, x1: int | float, y1: int | float) -> tuple[int | float, int | float] | None:
    # y - y0 = m0(x - x0)
    # y - y1 = m1(x - x1)
    # -m0 * x + y = y0 - m0 * x0
    # -m1 * x + y = y1 - m1 * x1
    delta = m1 - m0
    if delta == 0:
        return None
    c0 = y0 - m0 * x0
    c1 = y1 - m1 * x1
    x = c0 - c1
    y = m1 * c0 - m0 * c1
    return x / delta, y / delta
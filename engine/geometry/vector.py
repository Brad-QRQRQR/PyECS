import math

def vector_add(vax: int | float, vay: int | float, vbx: int | float, vby: int | float) -> tuple[int | float, int | float]:
    return vax + vbx, vay + vby

def vector_sub(vax: int | float, vay: int | float, vbx: int | float, vby: int | float) -> tuple[int | float, int | float]:
    return vax - vbx, vay - vby

def vector_mul(vx: int | float, vy: int | float, scalar: int | float) -> tuple[int | float, int | float]:
    return scalar * vx, scalar * vy

def vector_dot(vax: int | float, vay: int | float, vbx: int | float, vby: int | float) -> int | float:
    return vax * vbx + vay * vby

def vector_angle(vax: int | float, vay: int | float, vbx: int | float, vby: int | float) -> float:
    return vector_dot(vax, vay, vbx, vby) / (vector_magnitude(vax, vay) * vector_magnitude(vbx, vby))

def vector_magnitude(vx: int | float, vy: int | float) -> int | float:
    return math.sqrt(vx * vx + vy * vy)

def vector_projection_magnitude(vax: int | float, vay: int | float, vbx: int | float, vby: int | float) -> int | float:
    return vector_dot(vax, vay, vbx, vby) / vector_magnitude(vbx, vby)

def vector_projection(vax: int | float, vay: int | float, vbx: int | float, vby: int | float) -> tuple[int | float, int | float]:
    portion = vector_dot(vax, vay, vbx, vby) / (vbx * vbx + vby * vby)
    return vector_mul(vbx, vby, portion)

def vector_get_left_norm(vx: int | float, vy: int | float) -> tuple[int | float, int | float]:
    return -vy, vx

def vector_get_right_norm(vx: int | float, vy: int | float) -> tuple[int | float, int | float]:
    return vy, -vx

def vector_reflect(vx: int | float, vy: int | float, norm: tuple[int | float, int | float]) -> tuple[int | float, int | float]:
    tmp = vector_mul(norm[0], norm[1], 2 * vector_dot(vx, vy, norm[0], norm[1]))
    return vector_sub(vx, vy, tmp[0], tmp[1])
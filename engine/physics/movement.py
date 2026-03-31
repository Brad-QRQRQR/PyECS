import engine.framework as framework
import engine.components as ecomp

def adjust_collider_outer_box(ecs: framework.Ecs, dt: float) -> None:
    for eid, comps in ecs.query_with_component(ecomp.Speed, ecomp.Acceleration, ecomp.Collider):
        speed: ecomp.Speed = comps[0]()
        acceleration: ecomp.Acceleration = comps[1]()
        collider: ecomp.Collider = comps[2]()
        x_move: float = (acceleration.ax * dt / 2 + speed.dx) * dt
        y_move: float = (acceleration.ay * dt / 2 + speed.dy) * dt
        if x_move < 0:
            collider.aabb_lower_p.x = collider.aabb_lower_p.x + x_move
        if y_move < 0:
            collider.aabb_lower_p.y = collider.aabb_lower_p.y + y_move
        collider.aabb_outer_box.width = collider.aabb_inner_box.width + abs(x_move)
        collider.aabb_outer_box.height = collider.aabb_inner_box.height + abs(y_move)
        

def move_with_speed(ecs: framework.Ecs, dt: float) -> None:
    for eid, comps in ecs.query_with_component(ecomp.Point, ecomp.Speed, ecomp.Acceleration):
        pos: ecomp.Point = comps[0]()
        speed: ecomp.Speed = comps[1]()
        acceleration: ecomp.Acceleration = comps[2]()
        pos.x += (acceleration.ax * dt / 2 + speed.dx) * dt
        pos.y += (acceleration.ay * dt / 2 + speed.dy) * dt
        speed.dx += acceleration.ax
        speed.dy += acceleration.ay

        # if ecs.has_component(eid, ecomp.SparkOption):
        #     print(pos, speed.dx * dt, speed.dy * dt, dt)

def gravitate(ecs: framework.Ecs, gravity: int | float = 10) -> None:
    for eid, comps in ecs.query_with_component(ecomp.Acceleration):
        acceleration: ecomp.Acceleration = comps[0]()
        acceleration.ay += gravity


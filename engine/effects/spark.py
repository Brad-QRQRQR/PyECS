import math

import engine.framework as framework
import engine.components as ecomp
import engine.render as rend
import engine.geometry as geo

def emit_spark(
    ecs: framework.Ecs,
    pos: ecomp.Point,
    velocity: ecomp.Velocity,
    acceleration: ecomp.Acceleration,
    color: ecomp.Color,
    spark_opt: ecomp.SparkOption,
    fade: ecomp.FadeRate,
    render: rend.RenderManager,
    layer: int
) -> int:
    radian = math.radians(velocity.angle)
    return ecs.register_entity(
        pos,
        ecomp.PointSet(
            [
                ecomp.Point(
                    pos.x + math.cos(radian) * velocity.v * spark_opt.scale,
                    pos.y + math.sin(radian) * velocity.v * spark_opt.scale
                ),
                ecomp.Point(
                    pos.x + math.cos(radian + math.pi / 2) * velocity.v * spark_opt.scale * spark_opt.width_factor,
                    pos.y + math.sin(radian + math.pi / 2) * velocity.v * spark_opt.scale * spark_opt.width_factor
                ),
                ecomp.Point(
                    pos.x - math.cos(radian) * velocity.v * spark_opt.scale * spark_opt.tail_factor,
                    pos.y - math.sin(radian) * velocity.v * spark_opt.scale * spark_opt.tail_factor
                ),
                ecomp.Point(
                    pos.x + math.cos(radian - math.pi / 2) * velocity.v * spark_opt.scale * spark_opt.width_factor,
                    pos.y + math.sin(radian - math.pi / 2) * velocity.v * spark_opt.scale * spark_opt.width_factor
                ),
            ]
        ),
        velocity,
        acceleration,
        ecomp.Speed(velocity.v * math.cos(radian), velocity.v * math.sin(radian)),
        color,
        spark_opt,
        fade,
        render.get_layer(layer)(),
        ecomp.Renderer(rend.RenderId.POLYGON),
        ecomp.RenderablePolygon()
    )

def spark_fade(ecs: framework.Ecs, dt: float) -> None:
    for eid, comps in ecs.query_with_component(ecomp.Point, ecomp.PointSet, ecomp.Speed, ecomp.Velocity, ecomp.FadeRate, ecomp.SparkOption):
        center: ecomp.Point = comps[0]()
        pset: ecomp.PointSet = comps[1]()
        speed: ecomp.Speed = comps[2]()
        vel: ecomp.Velocity = comps[3]()
        fade: ecomp.FadeRate = comps[4]()
        spark_opt: ecomp.SparkOption = comps[5]()

        spark_opt.scale -= fade.rate * dt

        if spark_opt.scale <= 0:
            ecs.mark_dead_entity(eid)
            continue

        radian = math.radians(vel.angle)

        pset.points[0].x = center.x + speed.dx * spark_opt.scale
        pset.points[0].y = center.y + speed.dy * spark_opt.scale

        pset.points[1].x = center.x + math.cos(radian + math.pi / 2) * vel.v * spark_opt.scale * spark_opt.width_factor
        pset.points[1].y = center.y + math.sin(radian + math.pi / 2) * vel.v * spark_opt.scale * spark_opt.width_factor

        pset.points[2].x = center.x - math.cos(radian) * vel.v * spark_opt.scale * spark_opt.tail_factor
        pset.points[2].y = center.y - math.sin(radian) * vel.v * spark_opt.scale * spark_opt.tail_factor

        pset.points[3].x = center.x + math.cos(radian - math.pi / 2) * vel.v * spark_opt.scale * spark_opt.width_factor
        pset.points[3].y = center.y + math.sin(radian - math.pi / 2) * vel.v * spark_opt.scale * spark_opt.width_factor

        
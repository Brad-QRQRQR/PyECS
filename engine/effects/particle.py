import engine.framework as framework
import engine.components as ecomp
import engine.render as rend

import engine.misc as misc

def emit_particle(
    ecs: framework.Ecs,
    pos: ecomp.Point,
    speed: ecomp.Speed,
    acceleration: ecomp.Acceleration,
    radius: ecomp.Radius,
    color: ecomp.Color,
    fade: ecomp.FadeRate,
    render: rend.RenderManager,
    layer: int,
) -> int:
    return ecs.register_entity(
        pos,
        speed,
        acceleration,
        radius,
        color,
        fade,
        ecomp.Renderer(rend.RenderId.CIRCLE),
        render.get_layer(layer)(),
        ecomp.RenderableCircle(),
    )

def particle_fade(ecs: framework.Ecs, dt: float) -> None:
    for eid, comps in ecs.query_with_component(ecomp.Radius, ecomp.FadeRate):
        radius: ecomp.Radius = comps[0]()
        fade: ecomp.FadeRate = comps[1]()
        radius.r -= fade.rate * dt
        if radius.r <= 0:
            ecs.mark_dead_entity(eid)

def lighting_particle_update(game_loop: misc.GameLoop, cur_eid: int, par_int: int) -> None:
    par_ent: framework.Entity = game_loop.ecs.get_entity(par_int) # type: ignore
    if par_ent.get(ecomp.Radius).r <= 0: # type: ignore
        game_loop.ecs.mark_dead_entity(cur_eid)
    else:
        cur_ent: framework.Entity = game_loop.ecs.get_entity(cur_eid) # type: ignore
        cur_radius: ecomp.Radius = cur_ent.get(ecomp.Radius) # type: ignore
        cur_comb: ecomp.Combination = cur_ent.get(ecomp.Combination) # type: ignore
        cur_radius.r -= par_ent.get(ecomp.FadeRate).rate * game_loop.time_step # type: ignore
        cur_comb.rel_x = -cur_radius.r
        cur_comb.rel_y = -cur_radius.r
        if cur_radius.r <= 0:
            game_loop.ecs.mark_dead_entity(cur_eid)    
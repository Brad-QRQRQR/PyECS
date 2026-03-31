import engine.framework as framework
import engine.components as ecomp
import engine.render as rend

def emit_circle_lighting(
    ecs: framework.Ecs,
    pos: ecomp.Point,
    radius: ecomp.Radius,
    color: ecomp.Color,
    lighting_shape: ecomp.LightingShape,
    render: rend.RenderManager,
    layer: int
) -> int:
    return ecs.register_entity(
        ecomp.Point(pos.x - radius.r, pos.y - radius.r),
        radius,
        color,
        lighting_shape,
        ecomp.Renderer(rend.RenderId.CIRCLE_LIGHTNING),
        render.get_layer(layer)()
    )
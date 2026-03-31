import engine.framework as framework
import engine.components as ecomp
import engine.render as rend
import engine.geometry as geo

class EngineDebuger:
    def __init__(self):
        self.entity_ids: list[int] = list()

    def create_collider_outline(self, ecs: framework.Ecs, render: rend.RenderManager, color: tuple[int, int, int] = (0, 0, 0)) -> None:
        for eid in self.entity_ids:
            ecs.mark_dead_entity(eid)
        self.entity_ids.clear()

        for eid, comps in ecs.query_with_component(ecomp.Collider):
            collider: ecomp.Collider = comps[0]()
            pset = [
                ecomp.Point(
                    collider.aabb_lower_p.x,
                    collider.aabb_lower_p.y
                ),
                ecomp.Point(
                    collider.aabb_lower_p.x + collider.aabb_outer_box.width,
                    collider.aabb_lower_p.y
                ),
                ecomp.Point(
                    collider.aabb_lower_p.x,
                    collider.aabb_lower_p.y + collider.aabb_outer_box.height
                ),
                ecomp.Point(
                    collider.aabb_lower_p.x + collider.aabb_outer_box.width,
                    collider.aabb_lower_p.y + collider.aabb_outer_box.height
                ),
            ]
            geo.sort_points_couterclockwise(pset)
            self.entity_ids.append(
                ecs.register_entity(
                    ecomp.PointSet(pset),
                    ecomp.Color(color[0], color[1], color[2]),
                    ecomp.RenderablePolygon(2),
                    render.get_layer(render.get_max_layer_idx())(),
                    ecomp.Renderer(rend.RenderId.POLYGON),
                )
            )
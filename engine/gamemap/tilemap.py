import csv

import engine.framework as framework
import engine.components as ecomp
import engine.render as rend
import engine.physics as phy

def tile_map_load_from_csv(ecs: framework.Ecs, renderer: rend.RenderManager, name: str, tile_set: str, tile_size: int = 16) -> None:
    with open("/".join(["assets/map/info", name + ".csv"]), "r", newline="") as file:
        reader = csv.reader(file)
        x: int = 0
        y: int = 0
        for row in reader:
            for tp in row:
                tp_v = int(tp)
                if tp_v < 0:
                    continue
                ecs.register_entity(
                    ecomp.Point(x, y),
                    ecomp.Rect(tile_size, tile_size),
                    ecomp.Renderable(
                        renderer.surf_pool.get_tag_id("map"),
                        renderer.surf_pool.get_sta_id("map", tile_set),
                        tp_v,
                    ),
                    ecomp.Transform(),
                    ecomp.Renderer(rend.RenderId.SURF),
                    renderer.get_layer(0)(),
                    ecomp.Tile(),
                )
                x += tile_size
            y += tile_size
            x = 0

def tile_map_load_collider_info_from_csv(ecs: framework.Ecs, collision_sys: phy.Collision, name: str, tile_size: int = 16) -> None:
    with open("/".join(["assets/map/info", name + ".csv"]), "r", newline="") as file:
        reader = csv.reader(file)
        res = []
        for row in reader:
            for coll_tp in row:
                res.append(int(coll_tp))

        for eid, comps in ecs.query_with_component(ecomp.Renderable, ecomp.Point, ecomp.Tile, to_cache = False):
            tile_id: int = comps[0].frame
            if res[tile_id] == -1:
                continue
            pos: ecomp.Point = comps[1]
            ecs.add_component(eid, ecomp.CollisionType(res[tile_id]))
            ecs.add_component(eid, collision_sys.get_tag_with(tile_id))
            ecs.add_component(eid, ecomp.Collider(ecomp.Point(pos.x, pos.y), ecomp.Rect(tile_size, tile_size), ecomp.Rect(tile_size, tile_size)))
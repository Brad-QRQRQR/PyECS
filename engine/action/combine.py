from typing import Callable, Any
import engine.framework as framework
import engine.components as ecomp

import engine

def add_combination(ecs: framework.Ecs, entity_id: int, combination: ecomp.Combination) -> None:
    ecs.add_component(entity_id, combination)

def update_combination(game_loop: engine.GameLoop, tag: type[Any], func: Callable | None = None) -> None:
    visited: set[int] = set()
    for eid, comps in game_loop.ecs.query_with_component(ecomp.Combination, tag):
        comb = comps[0]()
        if comb.root in visited or comb.root < 0:
            continue
        visited.add(comb.root)
        
        par_comb: ecomp.Combination = game_loop.ecs.get_entity(comb.root).get(ecomp.Combination)
        cur_comb_eid: int = par_comb.nxt
        cur_comb: ecomp.Combination
        
        while cur_comb_eid > -1:
            cur_comb: ecomp.Combination = game_loop.ecs.get_entity(cur_comb_eid).get(ecomp.Combination)
            cur_pos: ecomp.Point = game_loop.ecs.get_entity(cur_comb.val).get(ecomp.Point)
            par_pos: ecomp.Point = game_loop.ecs.get_entity(par_comb.val).get(ecomp.Point)

            if func:
                func(game_loop, cur_comb.val, par_comb.val)

            cur_pos.x = par_pos.x + cur_comb.rel_x
            cur_pos.y = par_pos.y + cur_comb.rel_y

            cur_comb_eid = cur_comb.nxt
            par_comb = cur_comb
            
                


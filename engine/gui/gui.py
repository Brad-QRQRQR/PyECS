import engine.framework as framework
import engine.components as ecomp
import engine.render as rend

def update_gui_with_scroll(ecs: framework.Ecs):
    scroll = rend.camera_get_scroll(ecs)
    for eid, comps in ecs.query_with_component(ecomp.Point, ecomp.Gui):
        pos: ecomp.Point = comps[0]()
        gui: ecomp.Gui = comps[1]()
        pos.x = gui.x + scroll[0]
        pos.y = gui.y + scroll[1]
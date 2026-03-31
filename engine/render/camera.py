import engine.framework as framework
import engine.components as ecomp

def build_camera(
    ecs: framework.Ecs,
    center: tuple[int | float, int | float],
    focus: tuple[int | float, int | float],
    scale: int | float,
    x_border: tuple[int, int],
    y_border: tuple[int, int],
    follow_factor: int | float = 5,
    zoom_factor: int | float = 1,
) -> int:
    return ecs.register_entity(
        ecomp.Point(center[0], center[1]),
        ecomp.CameraOption(
            focus[0],
            focus[1],
            scale,
            follow_factor=follow_factor,
            zoom_factor=zoom_factor,
            left_border=x_border[0],
            right_border=x_border[1],
            top_border=y_border[0],
            bottom_border=y_border[1],
        )
    )
    
def camera_change_foucs(ecs: framework.Ecs, focus_x: int | float, focus_y: int | float) -> None:
    for eid, comps in ecs.query_with_component(ecomp.CameraOption):
        camera: ecomp.CameraOption = comps[0]()
        camera.focus_x = focus_x
        camera.focus_y = focus_y

def camera_follow(ecs: framework.Ecs) -> None:
    for eid, comps in ecs.query_with_component(ecomp.Point, ecomp.CameraOption):
        center: ecomp.Point = comps[0]()
        camera: ecomp.CameraOption = comps[1]()
        camera.scroll_x += (camera.focus_x - camera.scroll_x - center.x) / camera.follow_factor
        camera.scroll_y += (camera.focus_y - camera.scroll_y - center.y) / camera.follow_factor
        camera.scroll_x = max(camera.scroll_x, camera.left_border)
        camera.scroll_x = min(camera.scroll_x, camera.right_border)
        camera.scroll_y = max(camera.scroll_y, camera.top_border)
        camera.scroll_y = min(camera.scroll_y, camera.bottom_border)

def camera_change_scale(ecs: framework.Ecs, scale: int | float) -> None:
    for eid, comps in ecs.query_with_component(ecomp.CameraOption):
        camera: ecomp.CameraOption = comps[0]()
        camera.scale = scale

def camera_zoom(ecs: framework.Ecs) -> None:
    for eid, comps in ecs.query_with_component(ecomp.CameraOption):
        camera: ecomp.CameraOption = comps[0]()
        camera.zoom_size += (camera.scale - camera.zoom_size) / camera.zoom_factor

def camera_get_scroll(ecs: framework.Ecs) -> tuple[int, int]:
    for eid, comps in ecs.query_with_component(ecomp.CameraOption):
        camera: ecomp.CameraOption = comps[0]()
        return (int(camera.scroll_x), int(camera.scroll_y))
    return (0, 0)
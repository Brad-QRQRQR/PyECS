import math
import heapq

from typing import Any

import engine.framework as framework
import engine.components as ecomp
import engine.geometry as geo

class Collision:
    def __init__(self, tot_types: int = 0, chunk_size: int = 64):
        self.__box: dict[tuple[int, int], list[tuple[Any, ...]]] = dict()
        self.__mask: list[int] = [0] * tot_types
        self.__tag_table: list[type[Any]] = list()
        self.__tagid: dict[type[Any], int] = dict()
        self.__checked: set[tuple[int, int]] = set()
        self.__tot = tot_types
        self.__chunk_size = chunk_size

    def build_mask(self, masks: list[int]) -> None:
        if len(masks) != self.__tot:
            print(f"The size of mask table must be {self.__tot}")
            return
        self.__mask = masks

    def build_tag_table(self, table: list[Any]) -> None:
        if len(table) != self.__tot:
            print(f"The size of table must be {self.__tot}")
            return
        self.__tag_table = table
        for idx, tag in enumerate(self.__tag_table):
            self.__tagid[tag] = idx

    def build_box(self, ecs: framework.Ecs) -> None:
        for eid, comps in ecs.query_with_component(ecomp.Collider, ecomp.CollisionType):
            collider: ecomp.Collider = comps[0]()
            coll_type: ecomp.CollisionType = comps[1]()
            lxid = int(collider.aabb_lower_p.x / self.__chunk_size)
            rxid = int(geo.rect_get_right(collider.aabb_lower_p, collider.aabb_outer_box) / self.__chunk_size)
            lyid = int(collider.aabb_lower_p.y / self.__chunk_size)
            ryid = int(geo.rect_get_bottom(collider.aabb_lower_p, collider.aabb_outer_box) / self.__chunk_size)
            # if eid == 0:
            #     print(collider.aabb_lower_p.x, collider.aabb_lower_p.y, lxid, rxid, lyid, ryid)
            # if collider.aabb_lower_p.x == 0 and collider.aabb_lower_p.y <= 260:
            #     print(collider.aabb_lower_p.x, collider.aabb_lower_p.y, lxid, rxid, lyid, ryid)
            for x in range(lxid, rxid + 1):
                for y in range(lyid, ryid + 1):
                    #if (collider.aabb_lower_p.x == 0 and collider.aabb_lower_p.y <= 260) or eid == 0:
                    #    print((x, y))
                    idx = (x, y)
                    self._put_in_box(idx, (eid, coll_type.val, collider.aabb_lower_p, collider.aabb_outer_box))

    def get_tag_id(self, tag: type[Any]) -> int:
        if tag not in self.__tagid:
            print(f"The {tag} is not set as a collider tag in collision system.")
            return -1
        return self.__tagid[tag]
    
    def get_tag_with(self, idx: int) -> type[Any] | None:
        if idx > self.__tot:
            return None
        return self.__tag_table[idx]

    def _put_in_box(self, idx: tuple[int, int], info: tuple[Any, ...]) -> None:
        if idx not in self.__box:
            self.__box[idx] = list()
        self.__box[idx].append(info)

    def _check_collision(self, ecs: framework.Ecs, box: list[tuple[Any, ...]]) -> None:
        box.sort(key = lambda info: info[2].x)
        test_que: list[tuple[int | float, tuple]] = []

        for info in box:
            while test_que and test_que[0][0] < info[2].x:
                heapq.heappop(test_que)
            mask = self.__mask[info[1]]
            for test_info_with_key in test_que:
                test_info: tuple = test_info_with_key[1]
                if (info[0], test_info[0]) in self.__checked or (mask >> test_info[1] & 1) == 0:
                    continue
                
                if aabb_detect(info[2], info[3], test_info[2], test_info[3]):
                    self.__checked.add((info[0], test_info[0]))
                    self.__checked.add((test_info[0], info[0]))
                    ecs.register_entity(
                        ecomp.CollisionEvent(info[0], test_info[0]),
                        self.__tag_table[info[1]](),
                    )
                    ecs.register_entity(
                        ecomp.CollisionEvent(test_info[0], info[0]),
                        self.__tag_table[test_info[1]](),
                    )
            heapq.heappush(test_que, (geo.rect_get_right(info[2], info[3]), info))

    def check_collision(self, ecs: framework.Ecs) -> None:
        self.__box.clear()
        self.__checked.clear()
        self.build_box(ecs)
        for box in self.__box.values():
            self._check_collision(ecs, box)

    def clear_evnet(self, ecs: framework.Ecs) -> None:
        for eid, comps in ecs.query_with_component(ecomp.CollisionEvent):
            ecs.mark_dead_entity(eid)


def aabb_detect(pa: ecomp.Point, rta: ecomp.Rect, pb: ecomp.Point, rtb: ecomp.Rect) -> bool:
    if pa.x + rta.width > pb.x and pb.x + rtb.width > pa.x:
        if pa.y + rta.height > pb.y and pb.y + rtb.height > pa.y:
            return True
    return False

def circle_to_circle_detect(pa: ecomp.Point, ra: ecomp.Radius, pb: ecomp.Point, rb: ecomp.Radius) -> bool:
    sqrdis: float = (pa.x - pb.x) ** 2 + (pa.y - pb.y) ** 2
    return sqrdis < (ra.r + rb.r) ** 2

def aabb_to_circle_detect(pa: ecomp.Point, rta: ecomp.Rect, pb: ecomp.Point, rb: ecomp.Radius) -> tuple[bool, tuple[float, float], float]:
    def get_x() -> int | float:
        right = geo.rect_get_right(pa, rta)
        left = pa.x
        if pb.x <= left:
            return left
        if pb.x <= right:
            return pb.x
        return right
    
    def get_y() -> int | float:
        bottom = geo.rect_get_bottom(pa, rta)
        top = pa.y
        if pb.y <= top:
            return top
        if pb.y <= bottom:
            return pb.y
        return bottom

    x = get_x()
    y = get_y()
    sqrdis = (x - pb.x) ** 2 + (y - pb.y) ** 2
    norm = (pb.x - x, pb.y - y)
    
    if norm[0] == 0 and norm[1] == 0:
        return sqrdis < rb.r ** 2, norm, 0

    norm = geo.vector_mul(norm[0], norm[1], 1 / geo.vector_magnitude(norm[0], norm[1]))
    depth = rb.r - math.sqrt(sqrdis)

    # print(x, y, pa.y, geo.rect_get_bottom(pa, rta), pa.x, geo.rect_get_right(pa, rta), pb.x, pb.y)

    return sqrdis < rb.r ** 2, norm, depth

def swept_aabb_detect(pa: ecomp.Point, rta: ecomp.Rect, spda: ecomp.Speed, pb: ecomp.Point, rtb: ecomp.Rect) -> tuple[float, int, int] | None:
    x_entry_dis: float
    x_exit_dis: float
    y_entry_dis: float
    y_exit_dis: float
    # find the displacement between near and far sides for both x and y
    if spda.dx > 0:
        x_entry_dis = pb.x - (pa.x + rta.width)
        x_exit_dis = (pb.x + rtb.width) - pa.x
    else:
        x_entry_dis = (pb.x + rtb.width) - pa.x
        x_exit_dis = pb.x - (pa.x + rta.width)
    if spda.dy > 0:
        y_entry_dis = pb.y - (pa.y + rta.height)
        y_exit_dis = (pb.y + rtb.height) - pa.y
    else:
        y_entry_dis = (pb.y + rtb.height) - pa.y
        y_exit_dis = pb.y - (pa.y + rta.height)

    x_entry: float
    x_exit: float
    y_entry: float
    y_exit: float
    # calculate the entry and exit time for both x and y
    # if there is no speed in x or y direction,
    # this means there is nowhere the two rectangles overlap in that direction,
    # so make entry time be -inf and exit time be inf, showing that it is not possible to happen
    if spda.dx == 0:
        # if they don't overlap in x direction and the speed of moving object is 0,
        # they must not collide each other
        if pa.x + rta.width <= pb.x or pa.x >= pb.x + rtb.width:
            return None
        x_entry = -math.inf
        x_exit = math.inf
    else:
        x_entry = x_entry_dis / spda.dx
        x_exit = x_exit_dis / spda.dx        
    if spda.dy == 0:
        # same reason as in x direction
        if pa.y + rta.height <= pb.y or pa.y >= pb.y + rtb.height:
            return None
        y_entry = -math.inf
        y_exit = math.inf
    else:
        y_entry = y_entry_dis / spda.dy
        y_exit = y_exit_dis / spda.dy

    # when two rectangles start to collide with each other,
    # they must be overlapping in the two direction,
    # so take the maximum between two entry time
    entry_time: float = max(x_entry, y_entry)
    # if they are not overlapping in any one of direction,
    # so take the minimum between two exit time
    exit_time: float = min(x_exit, y_exit)

    # the length of interval [entry time, exit time] must be nonzero;
    # otherwise they don't collide at all
    # also, if entry time is bigger than 1,
    # this means they still need to move more to overlap in one of direction
    if entry_time > exit_time or entry_time > 1 or entry_time < 0:
        return None
        
    normal_x: int = 0
    normal_y: int = 0
    # determine which side is collided
    if x_entry > y_entry:
        normal_x = -1 if spda.dx > 0 else 1
    elif x_entry == y_entry:
        normal_x = -1 if spda.dx > 0 else 1
        normal_y = -1 if spda.dy > 0 else 1
    else:
        normal_y = -1 if spda.dy > 0 else 1

    return entry_time, normal_x, normal_y

def get_min_max_proj(pset: list[ecomp.Point], line: tuple[float, float]) -> tuple[float, float]:
    mn: float = math.inf
    mx: float = -math.inf
    for pt in pset:
        proj_mag: float = geo.vector_projection_magnitude(pt.x, pt.y, line[0], line[1])
        mn = min(mn, proj_mag)
        mx = max(mx, proj_mag)
    return mn, mx

def sat_detect(pset_a: list[ecomp.Point], pset_b: list[ecomp.Point]) -> tuple[bool, tuple[float, float], float] | None:
    def get_seperate_line(pset: list[ecomp.Point]) -> list[tuple[int | float, int | float]]:
        def get_norm(vx: int | float, vy: int | float) -> tuple[int | float, int | float]:
            v = geo.vector_get_left_norm(vx, vy)
            v = geo.vector_mul(v[0], v[1], 1 / geo.vector_magnitude(v[0], v[1]))
            return v
        return [
            get_norm(pt.x - pset[(idx + 1) % len(pset)].x, pt.y - pset[(idx + 1) % len(pset)].y)
            for idx, pt in enumerate(pset)
        ]
    
    geo.sort_points_couterclockwise(pset_a)
    geo.sort_points_couterclockwise(pset_b)
    projection_line = get_seperate_line(pset_a) + get_seperate_line(pset_b)
    min_dep: float = math.inf
    norm: tuple[float, float] = (0, 0)
    for line in projection_line:
        proj_a: tuple[float, float] = get_min_max_proj(pset_a, line)
        proj_b: tuple[float, float] = get_min_max_proj(pset_b, line)
        # print(line, proj_a, proj_b)
        if proj_b[0] >= proj_a[1] or proj_a[0] >= proj_b[1]:
            return None
        dep = min(proj_a[1] - proj_b[0], proj_b[1] - proj_a[0])
        if min_dep > dep:
            min_dep = dep
            norm = line

    cx_a = sum(pt.x for pt in pset_a) / len(pset_a)
    cy_a = sum(pt.y for pt in pset_a) / len(pset_a)
    cx_b = sum(pt.x for pt in pset_b) / len(pset_b)
    cy_b = sum(pt.y for pt in pset_b) / len(pset_b)

    cv = geo.vector_sub(cx_a, cy_a, cx_b, cy_b)
    if geo.vector_dot(cv[0], cv[1], norm[0], norm[1]) < 0:
        norm = (-norm[0], -norm[1])

    return True, norm, min_dep
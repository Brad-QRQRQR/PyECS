from dataclasses import dataclass

import engine.components as ecomp

@dataclass
class AABBNode:
    lower_p: ecomp.Point
    upper_p: ecomp.Point
    index: int
    parent: int
    left_child: int
    right_child: int
    is_leaf: bool

class AABBTree:
    def __init__(self, root_index: int):
        self.nodes: list[AABBNode] = list()
        self.root_index: int = root_index
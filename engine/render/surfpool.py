from typing import Any

import json

import pygame

class SurfPool:
    def __init__(self):
        # (tag, sta) [frame]
        self.__pool: dict[tuple[int, int], list[pygame.Surface]] = dict()
        self.__frames: dict[tuple[int, int], int] = dict()
        self.__tag_table: dict[str, int] = dict()
        self.__tag_cnt: int = 0
        self.__comb_table: dict[str, dict[str, int]] = dict()
        self.__transform_pool: dict[tuple[int, int, int], dict[tuple[int, int, bool, bool], pygame.Surface]] = dict()
    
    def get_tag_id(self, tag: str) -> int:
        return self.__tag_table[tag]
    
    def get_sta_id(self, tag: str, sta: str) -> int:
        if tag not in self.__comb_table:
            print(f"SurfPool::get_sta_id() error: the tag {tag} does not exist.")
            return -1
        if sta not in self.__comb_table[tag]:
            print(f"SurfPool::get_sta_id() error: the status {sta} does not exist.")
            return -1
        return self.__comb_table[tag][sta]

    def get_surf(self, tupid: tuple[int, int], frame: int) -> pygame.Surface:
        return self.__pool[tupid][frame]
    
    def get_transform_surf(self, surf_id: tuple[int, int, int], trans_param: tuple[int, int, bool, bool]) -> pygame.Surface | None:
        if surf_id not in self.__transform_pool or trans_param not in self.__transform_pool[surf_id]:
            return None
        return self.__transform_pool[surf_id][trans_param]
    
    def set_transform_surf(self, surf_id: tuple[int, int, int], trans_param: tuple[int, int, bool, bool], surf: pygame.Surface) -> None:
        if surf_id not in self.__transform_pool:
            self.__transform_pool[surf_id] = dict()
        self.__transform_pool[surf_id].setdefault(trans_param, surf)

    def load_surf(self, root_dir: str) -> None:
        for tag, sta_table in self.__comb_table.items():
            tag_v: int = self.__tag_table[tag]
            for sta, sta_v in sta_table.items():
                target: tuple[int, int] = (tag_v, sta_v)
                tot_f: int = self.__frames[target]
                self.__pool[target] = [
                    pygame.image.load(
                        "/".join([root_dir, tag, sta, sta + "_" + str(f) +  ".png"])
                    ).convert()
                    for f in range(tot_f)
                ]
                for surf in self.__pool[target]:
                    surf.set_colorkey((0, 0, 0))
    
    def load_info_from_json(self, path: str) -> None:
        sta_cnt: int = 0
        with open(path + ".json", mode = "r") as file:
            content: dict[str, list[list]] = json.load(file)
            for tag, stas in content.items():
                self.__tag_table[tag] = self.__tag_cnt
                
                sta_cnt = 0
                table: dict[str, int] = dict()
                for sta, frame in stas:
                    table[sta] = sta_cnt
                    self.__frames[(self.__tag_cnt, sta_cnt)] = frame
                    sta_cnt += 1

                self.__comb_table[tag] = table
                self.__tag_cnt += 1
# my own ECS framework

from weakref import ref, ReferenceType

from typing import Any, Iterable

from collections import deque

class Ecs:
    def __init__(self):
        self.__entities: dict[int, Entity] = dict()
        self.__dead_entities: set[int] = set()
        self.__next_id: int = 0
        self.__id_pool: deque[int] = deque()
        self.__cache: dict[tuple[type[Any], ...], list[tuple[int, tuple[ReferenceType, ...]]]] = dict()
        self.__cache_upd_flag: dict[tuple[type[Any], ...], int] = dict()
        self.__component_in_cache: dict[type[Any], list[tuple[type[Any], ...]]] = dict()
        self.__component_table: dict[type[Any], set[int]] = dict()
        self.__new_buffer: dict[type[Any], set[int]] = dict()
        self.__del_buffer: dict[type[Any], set[int]] = dict()

    def add_component(self, entity_id: int, component_insta: object) -> None:
        if entity_id not in self.__entities:
            return
        self.__entities[entity_id].add(component_insta)
        component_type: type[Any] = type(component_insta)
        self._change_cache_upd_flag(component_type)
        self._component_add(self.__new_buffer, component_type, entity_id)
        self._component_add(self.__component_table, component_type, entity_id)
    
    def remove_component(self, entity_id: int, component_type: type[Any]) -> None:
        if entity_id not in self.__entities:
            return
        self.__entities[entity_id].remove(component_type)
        self._change_cache_upd_flag(component_type)
        self._component_add(self.__del_buffer, component_type, entity_id)
        self.__component_table[component_type].remove(entity_id)

    def _change_cache_upd_flag(self, component_type: type[Any]) -> None:
        if component_type not in self.__component_in_cache:
            return
        for cache_type in self.__component_in_cache[component_type]:
            self.__cache_upd_flag[cache_type] = 1

    def _component_add(self, buffer: dict[type[Any], set[int]], component_type: type[Any], entity_id: int) -> None:
        if component_type not in buffer:
            buffer.setdefault(component_type, set())
        buffer[component_type].add(entity_id)

    def register_entity(self, *component_instas: Any) -> int:
        entity_id: int = self.__next_id if not self.__id_pool else self.__id_pool.pop()
        self.__next_id += 1
        entity: Entity = Entity()
        for comp in component_instas:
            entity.add(comp)
            comp_type: type[Any] = type(comp)
            self._change_cache_upd_flag(comp_type)
            self._component_add(self.__component_table, comp_type, entity_id)
            self._component_add(self.__new_buffer, comp_type, entity_id)
        self.__entities[entity_id] = entity
        return entity_id

    def mark_dead_entity(self, entity_id: int) -> None:
        self.__dead_entities.add(entity_id)
        if entity_id in self.__entities:
            entity: Entity = self.__entities.get(entity_id) # type: ignore
            for comp_type in entity.get_component_types():
                if comp_type not in self.__component_in_cache:
                    continue
                for cache_type in self.__component_in_cache[comp_type]:
                    if self.__cache_upd_flag[cache_type] == 0:
                        self.__cache_upd_flag[cache_type] = 2

    def remove_dead_entities(self) -> None:
        for entity_id in self.__dead_entities:
            if entity_id not in self.__entities:
                print(f"Ecs::remove_dead_entities() error: the entity of ID {entity_id} does not exist.")
                continue
            for comp_type in self.__entities.get(entity_id).get_component_types(): # type: ignore
                self.__component_table[comp_type].remove(entity_id)
            for buffer in self.__new_buffer.values():
                buffer.discard(entity_id)
            for buffer in self.__del_buffer.values():
                buffer.discard(entity_id)
            self.__entities.pop(entity_id)
            self.__id_pool.append(entity_id)
        self.__dead_entities.clear()

    def _component_matches(self, table: dict[type[Any], set[int]], component_types: tuple[type[Any], ...]) -> set[int]:
        sz: int = len(component_types)
        matching: set[int] = set()
        if sz > 0 and all(comp in table for comp in component_types):
            if sz == 1:
                matching = table[component_types[0]]
            else:
                matching = set.intersection(
                    *[table[comp_type] for comp_type in component_types if comp_type in table]
                )
        return matching

    def query_with_component(self, *component_types: type[Any], to_cache: bool = True) -> Iterable[tuple[int, tuple[Any, ...]]]:
        if to_cache:
            if component_types not in self.__cache:
                self.__cache_upd_flag[component_types] = 0
                for comp_type in component_types:
                    if comp_type not in self.__component_in_cache:
                        self.__component_in_cache[comp_type] = list()
                    self.__component_in_cache[comp_type].append(component_types)
                
                matching: set[int] = self._component_matches(self.__component_table, component_types)
                cache: list[tuple[int, tuple[Any, ...]]] = [(entity_id, tuple(ref(comp) for comp in self.get_entity(entity_id).get_multiple(component_types))) for entity_id in matching] #type: ignore
                self.__cache[component_types] = cache
            elif self.__cache_upd_flag[component_types] == 1:
                cache: list[tuple[int, tuple[Any, ...]]] = self.__cache[component_types]
                self.__cache_upd_flag[component_types] = 0
                new_matching: set[int] = self._component_matches(self.__new_buffer, component_types)
                del_matching: set[int] = self._component_matches(self.__del_buffer, component_types)
                new_matching = new_matching.difference(del_matching)

                cache.extend([(entity_id, tuple(ref(comp) for comp in self.get_entity(entity_id).get_multiple(component_types))) for entity_id in new_matching]) #type: ignore

                start = 0
                end = len(cache) - 1
                while start <= end and (cache[end][0] in del_matching or cache[end][0] in self.__dead_entities or cache[end][1][0]() is None):
                    end -= 1
                while start < end:
                    if cache[start][0] in del_matching or cache[start][0] in self.__dead_entities or cache[start][1][0]() is None:
                        cache[start], cache[end] = cache[end], cache[start]
                        while start < end and (cache[end][0] in del_matching or cache[end][0] in self.__dead_entities or cache[end][1][0]() is None):
                            end -= 1
                    start += 1

                num = len(cache) - end - 1
                if num > 0:
                    del cache[-num:]
            elif self.__cache_upd_flag[component_types] == 2:
                self.__cache_upd_flag[component_types] = 0
                cache: list[tuple[int, tuple[Any, ...]]] = self.__cache[component_types]
                
                start = 0
                end = len(cache) - 1
                while start <= end and (cache[end][0] in self.__dead_entities or cache[end][1][0]() is None):
                    end -= 1
                while start < end:
                    if cache[start][0] in self.__dead_entities or cache[start][1][0]() is None:
                        cache[start], cache[end] = cache[end], cache[start]
                        while start < end and (cache[end][0] in self.__dead_entities or cache[end][1][0]() is None):
                            end -= 1
                    start += 1

                num = len(cache) - end - 1
                if num > 0:
                    del cache[-num:]
            yield from self.__cache[component_types]
        else:
            matching: set[int] = self._component_matches(self.__component_table, component_types)
            for entity_id in matching:
                entity: Entity = self.get_entity(entity_id) # type: ignore
                yield entity_id, tuple(entity.get(comp_type) for comp_type in component_types)

    def clear_buffer(self) -> None:
        for buffer in self.__new_buffer.values():
            buffer.clear()
        for buffer in self.__del_buffer.values():
            buffer.clear()

    def get_entity(self, entity_id: int) -> "Entity | None":
        return self.__entities.get(entity_id)
    
    def get_entites(self) -> Iterable[tuple[int, "Entity"]]:
        for entity_id, entity in self.__entities.items():
            yield entity_id, entity

    def get_dead_entity_ids(self) -> Iterable[int]:
        return self.__dead_entities

    def get_entities_size(self) -> int:
        return len(self.__entities)
    
    def get_dead_entities_size(self) -> int:
        return len(self.__dead_entities)
    
    def get_new_buffer(self, component_type: type[Any]) -> frozenset[int] | None:
        if component_type not in self.__new_buffer:
            return None
        return frozenset(self.__new_buffer[component_type])
    
    def get_del_buffer(self, component_type: type[Any]) -> frozenset[int] | None:
        if component_type not in self.__del_buffer:
            return None
        return frozenset(self.__del_buffer[component_type])
    
    def get_cache_size(self, *component_types: type[Any]) -> int:
        if component_types not in self.__cache:
            print(f"Ecs::get_cache_size() error: the cache of combination {component_types} does not exist.")
            return 0
        return len(self.__cache[component_types])
    
    def get_cache_entity_ids(self, *component_types: type[Any]) -> Iterable[int]:
        if component_types not in self.__cache:
            print(f"Ecs::get_cache_entity_ids() error: the cache of combination {component_types} does not exist.")
            return
        # print(len(self.__cache[component_types]))
        for info in self.__cache[component_types]:
            yield info[0]

    def get_cache_components(self, *component_types: type[Any]) -> Iterable[tuple[ReferenceType, ...]]:
        if component_types not in self.__cache:
            print(f"Ecs::get_cache_components() error: the cache of combination {component_types} does not exist.")
            return
        for info in self.__cache[component_types]:
            yield info[1]
    
    def has_entities(self, *entity_ids: int) -> bool:
        return all(eid in self.__entities for eid in entity_ids)
    
    def entities_exist(self, *entity_ids: int) -> bool:
        return all(eid in self.__entities and eid not in self.__dead_entities for eid in entity_ids)
    
    def has_component(self, entity_id: int, *component_types: type[Any]) -> bool:
        entity: Entity | None = self.get_entity(entity_id)
        if entity is None:
            print(f"Ecs::has_component() error: The entity of ID {entity_id} is not in the world.")
            return False
        return entity.has(*component_types)
    
    def has_cache(self, *component_types: type[Any]) -> bool:
        return component_types in self.__cache
    
    def cache_has_entities(self, component_types: tuple[type[Any], ...], *entity_ids: int) -> bool:
        if component_types not in self.__cache:
            print(f"Ecs::cache_has_entities() error: the cache of combination {component_types} does not exist.")
            return False
        return all(
            any(info[0] == eid and info[1][0]() is not None for info in self.__cache[component_types])
            for eid in entity_ids
        )

class Entity:
    def __init__(self):
        self.__components: dict[type[Any], Any] = dict()

    def add(self, component_insta: object) -> None:
        component_type: type[Any] = type(component_insta)
        if component_type in self.__components:
            return
        self.__components[component_type] = component_insta

    def remove(self, component_type: type[Any]) -> None:
        try:
            self.__components.pop(component_type)
        except KeyError:
            print(f"Entity::remove() error: the component {component_type} does not exist.")

    def get(self, component_type: type[Any]) -> Any | None:
        return self.__components.get(component_type)
    
    def get_multiple(self, component_types: tuple[type[Any], ...]) -> tuple[Any, ...]:
        return tuple(self.__components.get(comp_type) for comp_type in component_types)

    def get_component_types(self) -> tuple[type[Any], ...]:
        return tuple(comp_type for comp_type in self.__components.keys())
    
    def has(self, *component_types: type[Any]) -> bool:
        return all(ct in self.__components for ct in component_types)
    
    def show(self):
        print(self.__components)

def deref_all(refs: tuple[ReferenceType, ...]) -> list[Any]:
    return [re() for re in refs]
# my own ECS framework

from typing import Any, Iterable

from collections import deque

class Ecs:
    def __init__(self):
        self.__entities: dict[int, Entity] = dict()
        self.__dead_entities: set[int] = set()
        self.__next_id: int = 0
        self.__id_pool: deque[int] = deque()
        self.__cache: dict[tuple[type[Any], ...], EntityGroup] = dict()
        self.__component_table: dict[type[Any], set[int]] = dict()
        self.__new_buffer: dict[type[Any], set[int]] = dict()
        self.__del_buffer: dict[type[Any], set[int]] = dict()
        # self.__cache_match: dict[tuple[type[Any], ...], set[tuple[type[Any], ...]]] = dict()
        self.__entity_in_caches: dict[int, set[tuple[type[Any], ...]]] = dict()

    def add_component(self, entity_id: int, component_insta: object) -> None:
        if entity_id not in self.__entities:
            return
        self.__entities[entity_id].add(component_insta)
        component_type: type[Any] = type(component_insta)
        self._component_add(self.__new_buffer, component_type, entity_id)
        self._component_add(self.__component_table, component_type, entity_id)
    
    def remove_component(self, entity_id: int, component_type: type[Any]) -> None:
        if entity_id not in self.__entities:
            return
        self.__entities[entity_id].remove(component_type)
        self._component_add(self.__del_buffer, component_type, entity_id)
        self.__component_table[component_type].remove(entity_id)

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
            self._component_add(self.__component_table, comp_type, entity_id)
            self._component_add(self.__new_buffer, comp_type, entity_id)
        self.__entities[entity_id] = entity
        # component_types: tuple[type[Any], ...] = entity.get_component_types()
        # cache_match: dict[tuple[type[Any], ...], set[tuple[type[Any], ...]]] = self.__cache_match
        # if component_types in cache_match:   
        #     for query_comp_types in cache_match[component_types]:
        #         self.__cache[query_comp_types].add(entity_id, [entity.get(comp_type) for comp_type in component_types])
        return entity_id

    def mark_dead_entity(self, entity_id: int) -> None:
        self.__dead_entities.add(entity_id)

    def _cache_remove_dead_entities(self, entity_id: int) -> None:
        try:
            entity_in_caches: set[tuple[type[Any], ...]] = self.__entity_in_caches[entity_id]
            for component_types in entity_in_caches:
                self.__cache[component_types].remove(entity_id)
            self.__entity_in_caches.pop(entity_id)
        except KeyError:
            print(f"Ecs::_cache_remove_dead_entites() error: the entity of ID {entity_id} is not in any caches.")

    def remove_dead_entities(self) -> None:
        for entity_id in self.__dead_entities:
            try:
                if entity_id in self.__entities:
                    for comp_type in self.__entities.get(entity_id).get_component_types(): # type: ignore
                        self.__component_table[comp_type].remove(entity_id)
                for buffer in self.__del_buffer.values():
                    if entity_id in buffer:
                        buffer.remove(entity_id)
                self.__entities.pop(entity_id)
                self.__id_pool.append(entity_id)
                self._cache_remove_dead_entities(entity_id)
            except KeyError:
                print(f"Ecs::remove_dead_entities() error: the entity of ID {entity_id} does not exist.")
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

    def query_with_component(self, *component_types: type[Any], to_cache: bool = True) -> Iterable[tuple[int, list[Any]]]:
        if to_cache:
            # if component_types not in self.__cache:
            #     self.__cache[component_types] = EntityGroup(component_types)
            #     for entity_id, entity in self.__entities.items():
            #         if entity.has(*component_types):
            #             component_list: list[Any] = [entity.get(comp_type) for comp_type in component_types]
            #             self.__cache[component_types].add(entity_id, component_list)
            #             entity_comp_types: tuple[type[Any], ...] = entity.get_component_types()
            #             if entity_comp_types not in self.__cache_match:
            #                 self.__cache_match.setdefault(entity_comp_types, set())
            #             self.__cache_match[entity_comp_types].add(component_types)
            #             if entity_id not in self.__entity_in_caches:
            #                 self.__entity_in_caches.setdefault(entity_id, set())
            #             self.__entity_in_caches[entity_id].add(component_types)
            #             yield entity_id, component_list
            # else:
            #     cache: EntityGroup = self.__cache[component_types]
            #     for entity_id, components in cache.get_entities():
            #         yield entity_id, components
            if component_types not in self.__cache:
                cache: EntityGroup = EntityGroup(component_types)
                self.__cache[component_types] = cache
                matching: set[int] = self._component_matches(self.__component_table, component_types)

                for entity_id in matching:
                    entity: Entity = self.get_entity(entity_id) # type: ignore
                    component_list: list[Any] = [entity.get(comp_type) for comp_type in component_types]
                    cache.add(entity_id, component_list)
                    
                    if entity_id not in self.__entity_in_caches:
                        self.__entity_in_caches.setdefault(entity_id, set())
                    self.__entity_in_caches[entity_id].add(component_types)
            else:
                cache: EntityGroup = self.__cache[component_types]
                new_matching: set[int] = self._component_matches(self.__new_buffer, component_types)
                del_matching: set[int] = self._component_matches(self.__del_buffer, component_types)
                new_matching = new_matching.difference(del_matching)
                
                for entity_id in new_matching:
                    entity: Entity = self.get_entity(entity_id) # type: ignore
                    component_list: list[Any] = [entity.get(comp_type) for comp_type in component_types]
                    cache.add(entity_id, component_list)
                    
                    if entity_id not in self.__entity_in_caches:
                        self.__entity_in_caches.setdefault(entity_id, set())
                    self.__entity_in_caches[entity_id].add(component_types)

                for entity_id in del_matching:
                    cache.remove(entity_id)
                    self.__entity_in_caches[entity_id].remove(component_types)


            yield from self.__cache[component_types].get_entities()
        else:
            for entity_id, entity in self.__entities.items():
                if entity.has(*component_types):
                    yield entity_id, [entity.get(comp_type) for comp_type in component_types]

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
        for entity_id in self.__dead_entities:
            yield entity_id

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
    
    def get_cache(self, *component_types: type[Any]) -> "EntityGroup | None":
        if component_types not in self.__cache:
            print(f"Ecs::get_cache() error: The {component_types} cache is not set yet.")
            return None
        return self.__cache[component_types]
    
    def get_entity_in_caches(self, entity_id: int) -> list[tuple[type[Any], ...]] | None:
        if entity_id not in self.__entity_in_caches:
            print(f"Ecs::get_entity_in_caches() error: The {entity_id} is not in any caches.")
            return None
        return [comp_type for comp_type in self.__entity_in_caches[entity_id]]
    
    def get_cache_size(self, *component_types: type[Any]) -> int:
        if component_types in self.__cache:
            return len(self.__cache[component_types])
        else:
            print(f"Ecs::get_cache_size() error: The {component_types} is not in cache.")
            return 0
        
    def get_entity_in_caches_size(self, entity_id: int) -> int:
        if entity_id in self.__entity_in_caches:
            return len(self.__entity_in_caches[entity_id])
        else:
            print(f"Ecs::get_entity_in_caches_size() error: The entity of ID {entity_id} in not in any caches.")
            return 0
    
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

    def get_component_types(self) -> tuple[type[Any], ...]:
        return tuple([comp_type for comp_type in self.__components.keys()])
    
    def has(self, *component_types: type[Any]) -> bool:
        return all(ct in self.__components for ct in component_types)
    
    def show(self):
        print(self.__components)
    
class EntityGroup:
    """A cache for a group of entities
    """
    def __init__(self, tags: tuple[type[Any], ...]):
        self.__group: dict[int, list[Any]] = dict()
        self.__tags: tuple[type[Any], ...] = tags

    def add(self, entity_id: int, components: list[Any]) -> None:
        self.__group[entity_id] = components
    
    def remove(self, entity_id: int) -> None:
        try:
            self.__group.pop(entity_id)
        except KeyError:
            print(f"EntityGroup::remove() error: The entity {entity_id} is not found in the entity group {self.__tags}")

    def clear(self) -> None:
        self.__group.clear()

    def has_entities(self, *entity_ids: int) -> bool:
        return all(eid in self.__group for eid in entity_ids)
    
    def get_entities(self) -> Iterable[tuple[int, list[Any]]]:
        yield from self.__group.items()

    def get_components(self) -> Iterable[list[Any]]:
        return self.__group.values()

    def get_entity_ids(self) -> Iterable[int]:
        return self.__group.keys()

    def __len__(self) -> int:
        return len(self.__group)

class Processor:
    def process(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError
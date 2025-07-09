# my own ECS framework

from typing import Any, Iterable

from itertools import count

class ECS:
    def __init__(self):
        self.__entities: dict[int, Entity] = dict()
        self.__dead_entities: set[int] = set()
        self.__cnt: count[int] = count(0)

    def add_component(self, entity_id: int, component_insta: Any) -> None:
        self.__entities[entity_id].add(component_insta)
    
    def remove_component(self, entity_id: int, component_type: Any) -> None:
        self.__entities[entity_id].remove(component_type)

    def register_new_entity(self, *componets: Any) -> int:
        entity_id: int = next(self.__cnt)
        self.__entities[entity_id] = Entity()
        for comp in componets:
            self.__entities[entity_id].add(comp)
        return entity_id

    def mark_dead_entity(self, entity_id: int) -> None:
        self.__dead_entities.add(entity_id)

    def remove_dead_entity(self) -> None:
        for entity_id in self.__dead_entities:
            try:
                self.__entities.pop(entity_id)
            except KeyError:
                print(f"KeyError: the entity of ID {entity_id} does not exist.")

    def get_entity(self, entity_id: int) -> "Entity | None":
        return self.__entities.get(entity_id)
    
    def get_entites(self) -> Iterable[tuple[int, "Entity"]]:
        for entity_id, entity in self.__entities.items():
            yield entity_id, entity

    def get_dead_entitis(self) -> Iterable[int]:
        for entity_id in self.__dead_entities:
            yield entity_id
    
    def has_entity(self, entity_id: int) -> bool:
        return entity_id in self.__entities
    
    def entity_exists(self, entity_id: int) -> bool:
        return entity_id in self.__entities and entity_id not in self.__dead_entities
    
    def has_component(self, entity_id: int, component_type: type[Any]) -> bool:
        entity: Entity | None = self.get_entity(entity_id)
        if entity is None:
            return False
        return entity.has(component_type)

class Entity:
    def __init__(self):
        self.components: dict[type[Any], Any] = dict()

    def add(self, component_insta: object) -> None:
        component_type: type[Any] = type(component_insta)
        if component_type in self.components:
            return
        self.components[component_type] = component_insta

    def remove(self, component_type: type[Any]) -> None:
        try:
            self.components.pop(component_type)
        except KeyError:
            print(f"KeyError: the component {component_type} does not exist.")

    def get(self, component_type: type[Any]) -> Any | None:
        return self.components.get(component_type)
    
    def has(self, component_type: type[Any]) -> bool:
        return component_type in self.components
    
class EntityGroup:
    """A cache for a group of entities
    """
    def __init__(self):
        self.__group: set[int] = set()

    def add(self, world: ECS, *components: Any) -> None:
        self.__group.add(world.register_new_entity(components))
    
    def remove(self, world: ECS) -> None:
        for entity_id in world.get_dead_entitis():
            self.__group.discard(entity_id)
    
    def __iter__(self):
        for entity_id in self.__group:
            yield entity_id

class Processor:
    def process(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError
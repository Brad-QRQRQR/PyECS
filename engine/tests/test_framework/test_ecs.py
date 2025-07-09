from ...framework import *

from dataclasses import dataclass

class TestECS:
    def setup_method(self):
        self.ecs = ECS()
        assert self.ecs is not None
    
    def test_ecs_register_without_comp(self):
        entity_id = self.ecs.register_new_entity()
        assert type(entity_id) is int
        assert entity_id == 0

    def test_ecs_register_with_comp(self):
        entity_id = self.ecs.register_new_entity(C1(), C2())
        assert type(entity_id) is int
        assert entity_id == 0
        assert self.ecs.has_component(entity_id, C1) == True
        assert self.ecs.has_component(entity_id, C2) == True

    def test_ecs_add_comp(self):
        entity_id = self.ecs.register_new_entity()
        self.ecs.add_component(entity_id, C1())
        self.ecs.add_component(entity_id, C2())
        assert self.ecs.has_component(entity_id, C1) == True
        assert self.ecs.has_component(entity_id, C2) == True

        entity = self.ecs.get_entity(entity_id)
        assert type(entity) is Entity
        assert type(entity.get(C1)) is C1
        assert (v := entity.get(C1)) is not None and v.x == 0
        assert (v := entity.get(C1)) is not None and v.y == 0
        assert type(entity.get(C2)) is C2
        assert (v := entity.get(C2)) is not None and v.string == "C2"

    def test_ecs_remove_dead_entity(self):
        for i in range(3):
            self.ecs.register_new_entity()
        self.ecs.mark_dead_entity(0)
        self.ecs.mark_dead_entity(1)
        self.ecs.remove_dead_entity()
        assert self.ecs.has_entity(0) == False
        assert self.ecs.has_entity(1) == False

############
# component
############

@dataclass
class C1:
    x: int = 0
    y: int = 0

@dataclass
class C2:
    string: str = "C2"
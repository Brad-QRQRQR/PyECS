from ...framework import *

from dataclasses import dataclass

class TestECS:
    def setup_method(self):
        self.ecs = Ecs()
        assert self.ecs is not None
    
    def test_register_entity_without_component(self):
        e1 = self.ecs.register_entity()
        e2 = self.ecs.register_entity()
        assert self.ecs.has_entities(e1) is True
        assert self.ecs.has_entities(e1, e2) is True
        assert e1 == 0 and e2 == 1
    
    def test_register_entity_with_component(self):
        e1 = self.ecs.register_entity(C1())
        e2 = self.ecs.register_entity(C1(), C2())
        assert self.ecs.has_entities(e1) is True
        assert self.ecs.has_entities(e1, e2) is True
        assert e1 == 0 and e2 == 1

        v = self.ecs.get_entity(e1)
        assert v is not None and v.has(C1)
        v = self.ecs.get_entity(e2)
        assert v is not None and v.has(C2) and v.has(C1, C2)

        assert self.ecs.has_component(e1, C1) is True
        assert self.ecs.has_component(e2, C1, C2) is True

    def test_add_component(self):
        e1 = self.ecs.register_entity()
        self.ecs.add_component(e1, C1())
        self.ecs.add_component(e1, C2())
        assert self.ecs.has_component(e1, C1, C2) is True
        self.ecs.add_component(e1, C1(1, 1))
        assert self.ecs.has_component(e1, C1, C2) is True
        assert (v := self.ecs.get_entity(e1)) is not None and v.get(C1).x == 0 and v.get(C1).y == 0 # type: ignore

    def test_remove_component(self):
        e1 = self.ecs.register_entity(C1(), C2(), C3(), C4())
        self.ecs.remove_component(e1, C1)
        assert self.ecs.has_component(e1, C1) is False
        self.ecs.remove_component(e1, C2)
        assert self.ecs.has_component(e1, C2) is False
        assert self.ecs.has_component(e1, C3) is True and self.ecs.has_component(e1, C4) is True
        assert self.ecs.has_component(e1, C1) is False

    def test_add_and_remove_component(self):
        e1 = self.ecs.register_entity()
        self.ecs.add_component(e1, C1())
        self.ecs.add_component(e1, C2())
        self.ecs.add_component(e1, C3())
        self.ecs.add_component(e1, C4())
        self.ecs.remove_component(e1, C1)
        assert self.ecs.has_component(e1, C2, C3, C4) is True and self.ecs.has_component(e1, C1) is False
        self.ecs.add_component(e1, C1(1, 1))
        assert self.ecs.has_component(e1, C1) is True
        assert self.ecs.get_entity(e1).get(C1).x == 1 and self.ecs.get_entity(e1).get(C1).y == 1 # type: ignore
        self.ecs.get_entity(e1).show() # type: ignore

    def test_mark_dead_entities(self):
        for _ in range(5):
            self.ecs.register_entity()
        lst = [0, 0, 1, 3]
        for i in lst:
            self.ecs.mark_dead_entity(i)
        assert self.ecs.get_dead_entities_size() == 3
        for eid in self.ecs.get_dead_entity_ids():
            assert eid in lst

    def test_remove_dead_entities(self):
        for _ in range(6):
            self.ecs.register_entity()
        lst = [0, 1, 2]
        for i in lst:
            self.ecs.mark_dead_entity(i)
        self.ecs.remove_dead_entities()
        assert self.ecs.get_dead_entities_size() == 0
        assert self.ecs.has_entities(3, 4) is True
        assert self.ecs.has_entities(0) is False
        assert self.ecs.has_entities(1) is False
        assert self.ecs.has_entities(2) is False

        self.ecs.mark_dead_entity(0)
        self.ecs.remove_dead_entities()
        assert self.ecs.has_entities(3, 4) is True
        assert self.ecs.has_entities(0) is False
        assert self.ecs.has_entities(1) is False
        assert self.ecs.has_entities(2) is False

    def test_has_component(self):
        e = self.ecs.register_entity(C1(), C2())
        assert self.ecs.has_component(e, C1, C2) is True

    def test_has_entites(self):
        lst = []
        for _ in range(5):
            lst.append(self.ecs.register_entity())
        assert self.ecs.has_entities(*[id for id in lst])

    def test_entities_exist(self):
        lst = []
        for _ in range(5):
            lst.append(self.ecs.register_entity())
        lst.pop()
        self.ecs.mark_dead_entity(lst.pop())
        self.ecs.mark_dead_entity(lst.pop())
        assert self.ecs.entities_exist(*[id for id in lst])

    def test_get_entity(self):
        e = self.ecs.register_entity()
        assert self.ecs.get_entity(e) is not None

    def test_get_entities_size(self):
        for _ in range(5):
            self.ecs.register_entity()
        assert self.ecs.get_entities_size() == 5
    
    def test_get_entites(self):
        for _ in range(5):
            self.ecs.register_entity(C1(), C2())
        lst = [0, 1, 2, 3, 4]
        for eid, e in self.ecs.get_entites():
            assert eid == lst[eid]
            assert e.has(C1, C2) is True

    def test_register_entity_and_remove_dead_entities(self):
        for _ in range(6):
            self.ecs.register_entity(C1(), C2())
        lst = [0, 2, 5]
        for i in lst:
            self.ecs.mark_dead_entity(i)
        self.ecs.remove_dead_entities()
        assert self.ecs.has_entities(1, 3, 4) is True
        assert self.ecs.has_entities(0) is False
        assert self.ecs.has_entities(2) is False
        assert self.ecs.has_entities(5) is False
        self.ecs.register_entity()
        assert self.ecs.has_entities(5) is True
        for _ in range(2):
            self.ecs.register_entity()
        assert self.ecs.has_entities(0, 1, 2, 3, 4, 5) is True
        for eid, e in self.ecs.get_entites():
            e.show()
            if eid in lst:
                assert e.has(C1) is False and e.has(C2) is False
            else:
                assert e.has(C1, C2) is True

    def test_get_dead_entities_size(self):
        for i in range(5):
            self.ecs.mark_dead_entity(i)
        assert self.ecs.get_dead_entities_size() == 5

    def test_get_dead_entity_ids(self):
        lst = [0, 1, 2]
        for i in lst:
            self.ecs.mark_dead_entity(i)
        ids = [i for i in self.ecs.get_dead_entity_ids()]
        assert self.ecs.get_dead_entities_size() == len(lst)
        ids = sorted(ids)
        assert ids == lst

    def test_query_with_component(self):
        for _ in range(6):
            self.ecs.register_entity(C1(), C2())
        for _ in range(6):
            self.ecs.register_entity(C2())
        
        lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        lst1 = [0, 1, 2, 3, 4, 5]
        lst2 = [6, 7, 8, 9, 10, 11]

        for _ in range(2):
            cnt = 0
            for eid, (c2,) in self.ecs.query_with_component(C2):
                assert eid in lst1 or eid in lst2
                assert type(c2) is C2
                cnt += 1

            assert cnt > 0

            g = self.ecs.get_cache(C2)
            assert g is not None
            assert list(g.get_entity_ids()) == lst
            assert self.ecs.get_cache_size(C2) == len(lst)

        for eid, (c1, c2) in self.ecs.query_with_component(C1, C2):
            assert type(c1) is C1 and type(c2) is C2
            assert eid in lst1

        g1 = self.ecs.get_cache(C1, C2)
        g2 = self.ecs.get_cache(C2, C1)
        assert g1 is not None and g2 is None
        assert g1 is not g2
        assert list(g1.get_entity_ids()) == lst1
        assert self.ecs.get_cache_size(C1, C2) != self.ecs.get_cache_size(C2, C1)

        for eid, (c2, c1) in self.ecs.query_with_component(C2, C1):
            assert type(c2) is C2 and type(c1) is C1
            assert eid in lst1
        
        g2 = self.ecs.get_cache(C2, C1)
        assert g2 is not None
        assert g1 is not g2
        assert list(g1.get_entity_ids()) == list(g2.get_entity_ids())
        assert self.ecs.get_cache_size(C1, C2) == self.ecs.get_cache_size(C2, C1)

    def test_get_new_buffer(self):
        st = self.ecs.get_new_buffer(C1)
        assert st is None
        
        for _ in range(5):
            self.ecs.register_entity(C1(), C2())
        lst = [0, 1, 2, 3, 4]
        st = self.ecs.get_new_buffer(C1)
        assert st is not None
        assert all(id in st for id in lst)

    def test_get_del_buffer(self):
        st = self.ecs.get_del_buffer(C1)
        assert st is None

        for _ in range(5):
            self.ecs.register_entity(C1(), C2())
        for i in range(5):
            self.ecs.remove_component(i, C2)
        
        st = self.ecs.get_del_buffer(C1)
        assert st is None

        st = self.ecs.get_del_buffer(C2)
        assert st is not None
        assert all(id in st for id in [0, 1, 2, 3, 4])
        
    def test_clear_buffer(self):
        for _ in range(6):
            self.ecs.register_entity(C1(), C2())
        for _ in range(3):
            self.ecs.register_entity(C3())
        lst = [0, 1, 2, 3, 4, 5]
        lst2 = [6, 7, 8]
        
        st = self.ecs.get_new_buffer(C1)
        assert st is not None
        assert all(id in st for id in lst) is True
        
        st = self.ecs.get_new_buffer(C2)
        assert st is not None
        assert all(id in st for id in lst) is True

        st = self.ecs.get_new_buffer(C3)
        assert st is not None
        assert all(id in st for id in lst2) is True

        self.ecs.clear_buffer()

        st = self.ecs.get_new_buffer(C1)
        assert st is not None
        assert len(st) == 0
        assert all(id in st for id in lst) is False
        
        st = self.ecs.get_new_buffer(C2)
        assert st is not None
        assert len(st) == 0
        assert all(id in st for id in lst) is False

        st = self.ecs.get_new_buffer(C3)
        assert st is not None
        assert len(st) == 0
        assert all(id in st for id in lst2) is False

    def test_register_entity_and_query_with_component(self):
        for _ in range(6):
            self.ecs.register_entity(C1(), C2())
        for _ in range(6):
            self.ecs.register_entity(C2(), C3())
        
        for eid, (c1,) in self.ecs.query_with_component(C1):
            pass

        self.ecs.clear_buffer()
        e = self.ecs.register_entity(C1())

        assert e == 12
        assert e in self.ecs.get_new_buffer(C1) # type: ignore

        for eid, (c1,) in self.ecs.query_with_component(C1):
            pass

        g = self.ecs.get_cache(C1)
        assert g is not None
        assert list(g.get_entity_ids()) == [0, 1, 2, 3, 4, 5, 12]

    def test_remove_component_and_query_with_component(self):
        lst = [] 
        for _ in range(6):
            lst.append(self.ecs.register_entity(C1(), C2()))

        e = lst.pop()
        self.ecs.remove_component(e, C1)

        for eid, (c1,) in self.ecs.query_with_component(C1):
            continue

        st = self.ecs.get_cache(C1)
        assert st is not None
        assert st.has_entities(*[id for id in lst]) is True
        assert st.has_entities(e) is False

        self.ecs.clear_buffer()

        e = lst.pop()
        self.ecs.remove_component(e, C1)

        for eid, (c1,) in self.ecs.query_with_component(C1):
            continue

        st = self.ecs.get_cache(C1)
        assert st is not None
        assert st.has_entities(*[id for id in lst]) is True
        assert st.has_entities(e) is False

    def test_add_component_and_query_with_component(self):
        lst = []
        lst2 = []
        for _ in range(6):
            lst.append(self.ecs.register_entity(C2()))

        e = lst.pop()
        lst2.append(e)
        self.ecs.add_component(e, C1())

        for eid, (c1,) in self.ecs.query_with_component(C1):
            continue

        st = self.ecs.get_cache(C1)
        assert st is not None
        assert st.has_entities(*lst2) is True

        for eid, (c1,) in st.get_entities():
            continue

        self.ecs.clear_buffer()

        e = lst.pop()
        lst2.append(e)
        self.ecs.add_component(e, C1())

        for eid, (c1,) in self.ecs.query_with_component(C1):
            continue

        st = self.ecs.get_cache(C1)
        assert st is not None
        assert st.has_entities(*lst2)

    def test_remove_dead_entities_and_query_with_component(self):
        lst = []
        for _ in range(6):
            lst.append(self.ecs.register_entity(C1()))

        lst2 = []
        for _ in range(3):
            e = lst.pop()
            self.ecs.mark_dead_entity(e)
            lst2.append(e)
        
        self.ecs.remove_dead_entities()

        cnt = 0
        for eid, (c1,) in self.ecs.query_with_component(C1):
            cnt += 1
        assert cnt > 0

        st = self.ecs.get_cache(C1)
        assert st is not None
        assert st.has_entities(*lst)

        self.ecs.clear_buffer()

        for _ in range(2):
            e = lst.pop()
            self.ecs.mark_dead_entity(e)
            lst2.append(e)
        
        self.ecs.remove_dead_entities()

        cnt = 0
        for eid, (c1,) in self.ecs.query_with_component(C1):
            cnt += 1
        assert cnt > 0

        st = self.ecs.get_cache(C1)
        assert st is not None
        assert st.has_entities(*lst)

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

@dataclass
class C3:
    a: int = 3
    b: int = 3

@dataclass
class C4:
    r: float = 4.5
    g: float = 3.3
    label: str = "C4"
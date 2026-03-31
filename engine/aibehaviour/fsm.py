from typing import Any
from typing import Callable

from weakref import ref, ReferenceType

import engine.framework as framework
import engine.components as ecomp

class Fsm:
    def __init__(self, tag: type[Any], tot_states: int):
        self.__tag = tag
        self.__tot_states = tot_states
        self.__enter_func: list[Callable[[int, ecomp.State, framework.Entity, float], None]] = [self._perform_nothing] * tot_states # type: ignore
        self.__exec_func: list[Callable[[int, ecomp.State, framework.Entity, float], None]] = [self._perform_nothing] * tot_states # type: ignore
        self.__exit_func: list[Callable[[int, ecomp.State, framework.Entity, float], None]] = [self._perform_nothing] * tot_states # type: ignore
        self.__state_id: dict[str, int] = dict()
        self.__state_group: list[list[tuple[int, ReferenceType[ecomp.State], ReferenceType[framework.Entity]]]] = [list() for _ in range(tot_states)]
        self.__transition: list[list[Callable[[ecomp.State], bool]]] = [[self._transit_nothing] * tot_states for _ in range(tot_states)]

    def _perform_nothing(self, entity_id: int, state: ecomp.State, entity: framework.Entity, dt: float) -> None:
        raise ValueError(f"There exists a function not registered yet.")
    
    def _transit_nothing(self, state: ecomp.State) -> bool:
        raise ValueError(f"There exists a transtion function not registered yet.")

    def build_state_id(self, states: list[str]) -> None:
        if len(states) != self.__tot_states:
            raise ValueError(f"Fsm::build_state_id() error: The total states must be {self.__tot_states}")
        for idx, state in enumerate(states):
            self.__state_id[state] = idx

    def register_on_state_enter(self, state: str, func: Callable) -> None:
        if state not in self.__state_id:
            raise KeyError(f"Fsm::register_on_state_enter() error: The state {state} is not in the FSM.")
        self.__enter_func[self.__state_id[state]] = func
    
    def register_on_state_exec(self, state: str, func: Callable) -> None:
        if state not in self.__state_id:
            raise KeyError(f"Fsm::register_on_state_exec() error: The state {state} is not in the FSM.")
        self.__exec_func[self.__state_id[state]] = func

    def register_on_state_exit(self, state: str, func: Callable) -> None:
        if state not in self.__state_id:
            raise KeyError(f"Fsm::register_on_state_exit() error: The state {state} is not in the FSM.")
        self.__exit_func[self.__state_id[state]] = func

    def add_entity(self, ecs: framework.Ecs, entity_id: int) -> None:
        entity: framework.Entity = ecs.get_entity(entity_id)
        state: ecomp.State = entity.get(self.__tag)
        self.__state_group[state.state_id].append(
            (
                entity_id,
                ref(state),
                ref(entity),
            )
        )

    def listen_trans(self, ecs: framework.Ecs, dt: float) -> None:
        buffer: list[list[tuple[int, ReferenceType[ecomp.State], ReferenceType[framework.Entity]]]] = [list() for _ in range(self.__tot_states)]
        for grp in self.__state_group:
            start: int = 0
            end: int = len(grp) - 1
            while start <= end and (grp[end][1]() is None or not ecs.entities_exist(grp[end][0])):
                end -= 1
            while start < end:
                state: ecomp.State | None = grp[start][1]() # type: ignore
                if state is None:
                    grp[start], grp[end] = grp[end], grp[start]
                    while start < end and (grp[end][1]() is None or not ecs.entities_exist(grp[end][0])):
                        end -= 1
            num: int = len(grp) - end - 1
            if num > 0:
                del grp[-num:]

        for grp in self.__state_group:
            for info in grp:
                run: bool = True
                entity_id: int = info[0]
                state: ecomp.State = info[1]() # type: ignore
                entity: framework.Entity = info[2]() # type: ignore
                while run:
                    run = False
                    for nsid, trans in enumerate(self.__transition[state.state_id]):
                        if trans(state):
                            self.__exit_func[state.state_id](entity_id, state, entity, dt)
                            state.state_id = nsid
                            self.__enter_func[state.state_id](entity_id, state, entity, dt)
                            run = True
                            break
                buffer[state.state_id].append(info)

        for sid, grp in enumerate(self.__state_group):
            grp += buffer[sid]

    def update(self, dt: float) -> None:
        for sid, grp in enumerate(self.__state_group):
            for info in grp:
                self.__exec_func[sid](info[0], info[1](), info[2](), dt) # type: ignore
    
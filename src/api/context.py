import contextvars
from typing import Any, Callable, Dict, List

from fvalues import F


class LocalState:
    _context_var: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar(
        "local_state"
    )

    _str: Callable[[Any], str] = str

    def __init__(self, initial_state, _str: Callable[[Any], str] = str):
        self.initial_state = initial_state
        self._str = _str  # type: ignore

    def __str__(self):
        return str({k: self._str(v) for k, v in self.initial_state.items()}).strip("{}")

    def __enter__(self):
        self.token = self._context_var.set(self.initial_state)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._context_var.reset(self.token)
        return False  # Allows exceptions to propagate, if any occur within the block

    @classmethod
    def get(cls, key, default=None):
        state = cls._context_var.get(None)
        if state is None:
            return default
        return state.get(key, default)

    @classmethod
    def set(cls, key, value):
        state = cls._context_var.get(None)
        if state is not None:
            state[key] = value

    @classmethod
    def dump(cls):
        return cls._context_var.get(None)


class LocalStateList(LocalState):
    def __init__(self, initial_state, _str: Callable[[Any], str] = str):
        if not isinstance(initial_state, list):
            raise ValueError("initial_state must be a list")
        super().__init__(initial_state, _str)

    def __str__(self):
        # TODO: this is hard-coded!!!
        res = ["Previous action/result/justification steps."] + [
            self._str(v) for v in self.initial_state
        ]
        return F("\n").join(res).strip()

    @classmethod
    def get(cls, index, default=None):
        state = cls._context_var.get(None)
        if state is None or index >= len(state):
            return default
        return state[index]

    @classmethod
    def set(cls, index, value):
        state = cls._context_var.get(None)
        if state is not None and index < len(state):
            state[index] = value

    @classmethod
    def append(cls, value):
        state = cls._context_var.get(None)
        if state is not None:
            state.append(value)


# # Functions that read, update, and dump LocalState
# def read_from_local_state(key):
#     return LocalState.get(key)


# def update_local_state(key, value):
#     LocalState.set(key, value)


# def dump_local_state():
#     return LocalState.dump()


# Usage example
# initial_state = {"x": 10, "y": 20}

# with LocalState(initial_state):
#     print(read_from_local_state("x"))  # Prints 10
#     print(read_from_local_state("y"))  # Prints 20

#     print(dump_local_state())  # Prints {'x': 10, 'y': 20}

# initial_state_list = [10, 20, 30]

# with LocalStateList(initial_state_list) as state:
#     print(state.get(0))  # Prints 10
#     print(state.get(1))  # Prints 20

#     print(state.dump())  # Prints [10, 20, 30]

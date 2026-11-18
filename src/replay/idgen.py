import uuid
from typing import Protocol


class IdGen(Protocol):
    def new_id(self) -> str:
        ...


class SystemIdGen:
    def new_id(self) -> str:
        return str(uuid.uuid4())


class FakeIdGen:
    def __init__(self) -> None:
        self._counter = 0

    def new_id(self) -> str:
        self._counter += 1
        return f"fake-id-{self._counter}"
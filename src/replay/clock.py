from datetime import UTC, datetime, timedelta
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class FakeClock:
    def __init__(self, initial_time: datetime) -> None:
        self._current_time = initial_time

    def now(self) -> datetime:
        return self._current_time

    def advance(self, delta: timedelta) -> None:
        self._current_time += delta
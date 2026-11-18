from datetime import UTC, datetime, timedelta

from replay.clock import FakeClock, SystemClock


def test_fake_clock_returns_initial_time() -> None:
    initial_time = datetime(2026, 1, 1, tzinfo=UTC)
    clock = FakeClock(initial_time)

    assert clock.now() == initial_time


def test_fake_clock_can_advance() -> None:
    initial_time = datetime(2026, 1, 1, tzinfo=UTC)
    clock = FakeClock(initial_time)

    clock.advance(timedelta(seconds=30))

    assert clock.now() == initial_time + timedelta(seconds=30)


def test_system_clock_returns_utc_time() -> None:
    clock = SystemClock()

    assert clock.now().tzinfo == UTC

import pytest

from replay.state_machine import RunStatus, transition


def test_pending_can_transition_to_running() -> None:
    assert (
        transition(RunStatus.PENDING, RunStatus.RUNNING)
        == RunStatus.RUNNING
    )


def test_running_can_transition_to_waiting_approval() -> None:
    assert (
        transition(RunStatus.RUNNING, RunStatus.WAITING_APPROVAL)
        == RunStatus.WAITING_APPROVAL
    )


def test_running_can_transition_to_succeeded() -> None:
    assert (
        transition(RunStatus.RUNNING, RunStatus.SUCCEEDED)
        == RunStatus.SUCCEEDED
    )


def test_waiting_approval_can_resume() -> None:
    assert (
        transition(RunStatus.WAITING_APPROVAL, RunStatus.RUNNING)
        == RunStatus.RUNNING
    )


def test_succeeded_is_terminal() -> None:
    with pytest.raises(ValueError):
        transition(RunStatus.SUCCEEDED, RunStatus.RUNNING)


def test_failed_is_terminal() -> None:
    with pytest.raises(ValueError):
        transition(RunStatus.FAILED, RunStatus.RUNNING)


def test_dead_is_terminal() -> None:
    with pytest.raises(ValueError):
        transition(RunStatus.DEAD, RunStatus.RUNNING)


def test_pending_cannot_skip_to_succeeded() -> None:
    with pytest.raises(ValueError):
        transition(RunStatus.PENDING, RunStatus.SUCCEEDED)

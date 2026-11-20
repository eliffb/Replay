
from enum import StrEnum


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DEAD = "dead"


ALLOWED_TRANSITIONS: dict[RunStatus, set[RunStatus]] = {
    RunStatus.PENDING: {
        RunStatus.RUNNING,
    },
    RunStatus.RUNNING: {
        RunStatus.WAITING_APPROVAL,
        RunStatus.SUCCEEDED,
        RunStatus.FAILED,
        RunStatus.DEAD,
    },
    RunStatus.WAITING_APPROVAL: {
        RunStatus.RUNNING,
        RunStatus.FAILED,
        RunStatus.DEAD,
    },
    RunStatus.SUCCEEDED: set(),
    RunStatus.FAILED: set(),
    RunStatus.DEAD: set(),
}


def transition(
    current: RunStatus,
    target: RunStatus,
) -> RunStatus:
    if target not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(
            f"Invalid run transition: {current.value} -> {target.value}"
        )

    return target


from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = Field(default=1, ge=1)


class RunCreated(EventBase):
    event_type: Literal["RunCreated"] = "RunCreated"
    run_id: str
    input: dict[str, object] = Field(default_factory=dict)


class StepStarted(EventBase):
    event_type: Literal["StepStarted"] = "StepStarted"
    run_id: str
    step_no: int = Field(ge=1)


class LlmRequested(EventBase):
    event_type: Literal["LlmRequested"] = "LlmRequested"
    run_id: str
    step_no: int = Field(ge=1)
    request: dict[str, object]


class LlmResponded(EventBase):
    event_type: Literal["LlmResponded"] = "LlmResponded"
    run_id: str
    step_no: int = Field(ge=1)
    response: dict[str, object]


class ToolRequested(EventBase):
    event_type: Literal["ToolRequested"] = "ToolRequested"
    run_id: str
    step_no: int = Field(ge=1)
    tool_name: str
    tool_call_id: str
    arguments: dict[str, object]


class ToolResulted(EventBase):
    event_type: Literal["ToolResulted"] = "ToolResulted"
    run_id: str
    step_no: int = Field(ge=1)
    tool_call_id: str
    result: dict[str, object] = Field(default_factory=dict)


class StepCompleted(EventBase):
    event_type: Literal["StepCompleted"] = "StepCompleted"
    run_id: str
    step_no: int = Field(ge=1)


class RunFailed(EventBase):
    event_type: Literal["RunFailed"] = "RunFailed"
    run_id: str
    error_class: str
    error_message: str

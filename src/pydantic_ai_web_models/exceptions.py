"""Exception types for web model providers."""

from __future__ import annotations


class WebModelError(Exception):
    """Base exception for web model errors."""


class TemporalConnectionError(WebModelError):
    """Raised when the Temporal client cannot connect."""


class WorkflowExecutionError(WebModelError):
    """Raised when the LLMInvokeWorkflow returns an error."""

    def __init__(self, message: str, workflow_id: str | None = None):
        self.workflow_id = workflow_id
        super().__init__(message)


class JSONParseError(WebModelError):
    """Raised when structured output cannot be parsed as valid JSON."""

    def __init__(self, message: str, raw_text: str):
        self.raw_text = raw_text
        super().__init__(message)

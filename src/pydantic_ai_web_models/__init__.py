"""Pydantic AI Web Models -- use web-based LLMs via Temporal workflows."""

from .config import (
    AVAILABLE_MODELS,
    TemporalConfig,
    get_default_config,
    set_default_config,
)
from .exceptions import (
    JSONParseError,
    TemporalConnectionError,
    WebModelError,
    WorkflowExecutionError,
)
from .model import WebModel
from .registration import register_web_models

register_web_models()

__all__ = [
    "AVAILABLE_MODELS",
    "JSONParseError",
    "TemporalConfig",
    "TemporalConnectionError",
    "WebModel",
    "WebModelError",
    "WorkflowExecutionError",
    "get_default_config",
    "set_default_config",
]

"""Register openai-web and google-web providers with pydantic-ai."""

from __future__ import annotations

import logging
from typing import Any, Callable

from pydantic_ai import models

logger = logging.getLogger(__name__)

_prefix_registry: dict[str, Callable[[str], models.Model]] = {}
_original_infer: Callable[..., Any] | None = None
_is_patched: bool = False


def _register_model_prefix(prefix: str, factory: Callable[[str], models.Model]) -> None:
    """Register a model prefix with a factory function.

    The factory receives the full model string (e.g. 'openai-web:gpt-5-3')
    and must return a Model instance.
    """
    _prefix_registry[prefix] = factory
    _ensure_patched()
    logger.info("Registered model prefix: %s", prefix)


def _ensure_patched() -> None:
    """Patch infer_model once to handle all registered prefixes."""
    global _original_infer, _is_patched  # noqa: PLW0603

    if _is_patched:
        return

    _original_infer = models.infer_model

    def _patched_infer(model: models.Model | str) -> models.Model:
        if isinstance(model, models.Model):
            return model

        if isinstance(model, str):
            for prefix, factory in _prefix_registry.items():
                if model.startswith(f"{prefix}:"):
                    return factory(model)

        assert _original_infer is not None
        return _original_infer(model)

    models.infer_model = _patched_infer
    _is_patched = True


def _web_model_factory(model_string: str) -> models.Model:
    """Factory for web model strings like 'openai-web:gpt-5-3'."""
    parts = model_string.split(":", 1)
    if len(parts) != 2 or not parts[1]:
        raise ValueError(f"Invalid model string: {model_string!r}")

    provider, model_name = parts

    from .model import WebModel

    return WebModel(provider=provider, model_name=model_name)


def register_web_models() -> None:
    """Register openai-web and google-web prefixes with pydantic-ai."""
    _register_model_prefix("openai-web", _web_model_factory)
    _register_model_prefix("google-web", _web_model_factory)
    logger.info("Registered web model providers: openai-web, google-web")

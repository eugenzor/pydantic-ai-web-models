"""Configuration for web model providers and Temporal connection."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

AVAILABLE_MODELS: dict[str, list[str]] = {
    "google-web": ["gemini-3-flash", "gemini-3-flash-thinking", "gemini-3.1-pro"],
    "openai-web": ["gpt-5-3", "gpt-5-4-standard", "gpt-5-4-extended"],
}


class TemporalConfig(BaseSettings):
    """Temporal workflow and connection settings loaded from environment.

    The Temporal SDK's ``envconfig`` bridge handles ``TEMPORAL_ADDRESS`` and
    ``TEMPORAL_NAMESPACE`` natively.  TLS certificate paths and app-level
    workflow settings are not supported by the bridge, so we read them here
    via pydantic-settings.
    """

    model_config = SettingsConfigDict(
        env_prefix="TEMPORAL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App-level workflow settings
    task_queue: str = Field(default="ai-worker-task-queue")
    workflow_name: str = Field(default="LLMInvokeWorkflow")
    timeout_seconds: int = Field(default=300)

    # TLS settings (not handled by the SDK bridge)
    tls_cert: Path | None = Field(default=None)
    tls_key: Path | None = Field(default=None)
    tls_ca: Path | None = Field(default=None)
    tls_server_name: str | None = Field(default=None)


_default_config: TemporalConfig | None = None


def get_default_config() -> TemporalConfig:
    """Get the module-level default Temporal config, creating one if needed."""
    global _default_config  # noqa: PLW0603
    if _default_config is None:
        _default_config = TemporalConfig()
    return _default_config


def set_default_config(config: TemporalConfig) -> None:
    """Set the module-level default Temporal config."""
    global _default_config  # noqa: PLW0603
    _default_config = config

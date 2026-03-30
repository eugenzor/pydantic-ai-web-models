from pydantic_ai_web_models.config import (
    AVAILABLE_MODELS,
    TemporalConfig,
    get_default_config,
    set_default_config,
)


def test_available_models_has_expected_providers():
    assert "google-web" in AVAILABLE_MODELS
    assert "openai-web" in AVAILABLE_MODELS


def test_available_models_are_non_empty_lists():
    for provider, models in AVAILABLE_MODELS.items():
        assert isinstance(models, list), f"{provider} should map to a list"
        assert len(models) > 0, f"{provider} should have at least one model"


def test_temporal_config_defaults(monkeypatch):
    for var in (
        "TEMPORAL_TLS_CERT",
        "TEMPORAL_TLS_KEY",
        "TEMPORAL_TLS_CA",
        "TEMPORAL_TLS_SERVER_NAME",
    ):
        monkeypatch.delenv(var, raising=False)
    cfg = TemporalConfig(_env_file=None)
    assert cfg.task_queue == "ai-worker-task-queue"
    assert cfg.workflow_name == "LLMInvokeWorkflow"
    assert cfg.timeout_seconds == 300
    assert cfg.tls_cert is None
    assert cfg.tls_key is None
    assert cfg.tls_ca is None
    assert cfg.tls_server_name is None


def test_temporal_config_custom_values():
    cfg = TemporalConfig(
        task_queue="custom-queue",
        workflow_name="MyWorkflow",
        timeout_seconds=60,
        _env_file=None,
    )
    assert cfg.task_queue == "custom-queue"
    assert cfg.workflow_name == "MyWorkflow"
    assert cfg.timeout_seconds == 60


def test_get_default_config_returns_temporal_config():
    cfg = get_default_config()
    assert isinstance(cfg, TemporalConfig)


def test_get_default_config_is_singleton():
    cfg1 = get_default_config()
    cfg2 = get_default_config()
    assert cfg1 is cfg2


def test_set_default_config(reset_default_config):
    new_cfg = TemporalConfig(task_queue="override-queue", _env_file=None)
    set_default_config(new_cfg)
    assert get_default_config() is new_cfg
    assert get_default_config().task_queue == "override-queue"


def test_set_default_config_replaces_singleton(reset_default_config):
    first = get_default_config()
    new_cfg = TemporalConfig(_env_file=None)
    set_default_config(new_cfg)
    assert get_default_config() is not first
    assert get_default_config() is new_cfg

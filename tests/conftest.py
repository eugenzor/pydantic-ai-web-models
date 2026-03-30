import pytest
import pydantic_ai_web_models.config as config_module


@pytest.fixture()
def reset_default_config():
    """Restore the module-level default config after each test that changes it."""
    original = config_module._default_config
    yield
    config_module._default_config = original

import pytest

import pydantic_ai_web_models.registration as reg_module
from pydantic_ai_web_models.model import WebModel
from pydantic_ai_web_models.registration import _web_model_factory


# ---------------------------------------------------------------------------
# _web_model_factory
# ---------------------------------------------------------------------------


def test_factory_valid_openai():
    model = _web_model_factory("openai-web:gpt-5-3")
    assert isinstance(model, WebModel)
    assert model.model_name == "openai-web:gpt-5-3"


def test_factory_valid_google():
    model = _web_model_factory("google-web:gemini-3-flash")
    assert isinstance(model, WebModel)
    assert model.model_name == "google-web:gemini-3-flash"


def test_factory_no_colon_raises():
    with pytest.raises(ValueError):
        _web_model_factory("openai-web")


def test_factory_empty_model_name_raises():
    with pytest.raises(ValueError):
        _web_model_factory("openai-web:")


def test_factory_unknown_model_raises():
    with pytest.raises(ValueError, match="Unknown model"):
        _web_model_factory("openai-web:nonexistent-model")


def test_factory_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown provider"):
        _web_model_factory("unknown-provider:some-model")


# ---------------------------------------------------------------------------
# register_web_models / patching state
# ---------------------------------------------------------------------------


def test_both_prefixes_registered():
    assert "openai-web" in reg_module._prefix_registry
    assert "google-web" in reg_module._prefix_registry


def test_infer_model_is_patched():
    assert reg_module._is_patched is True


def test_patched_infer_model_resolves_openai_web():
    from pydantic_ai import models

    model = models.infer_model("openai-web:gpt-5-3")
    assert isinstance(model, WebModel)


def test_patched_infer_model_resolves_google_web():
    from pydantic_ai import models

    model = models.infer_model("google-web:gemini-3-flash")
    assert isinstance(model, WebModel)

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic_ai.messages import ModelRequest, TextPart, ToolCallPart, UserPromptPart

from pydantic_ai_web_models.config import TemporalConfig
from pydantic_ai_web_models.exceptions import WorkflowExecutionError
from pydantic_ai_web_models.model import WebModel

_CFG = TemporalConfig(_env_file=None)


def _make_model(provider="openai-web", model_name="gpt-5-3"):
    return WebModel(provider=provider, model_name=model_name, temporal_config=_CFG)


def _mock_client(response_payload: dict) -> MagicMock:
    """Return a mock Temporal client whose execute_workflow returns response_payload."""
    client = MagicMock()
    client.execute_workflow = AsyncMock(return_value=response_payload)
    return client


def _request_params(output_tools=None):
    params = MagicMock()
    params.output_tools = output_tools or []
    return params


# ---------------------------------------------------------------------------
# Constructor validation
# ---------------------------------------------------------------------------


def test_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown provider"):
        WebModel(provider="bad-provider", model_name="gpt-5-3", temporal_config=_CFG)


def test_unknown_model_raises():
    with pytest.raises(ValueError, match="Unknown model"):
        WebModel(provider="openai-web", model_name="gpt-99-ultra", temporal_config=_CFG)


def test_valid_construction_openai():
    model = _make_model("openai-web", "gpt-5-3")
    assert model is not None


def test_valid_construction_google():
    model = _make_model("google-web", "gemini-3-flash")
    assert model is not None


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------


def test_model_name_property():
    model = _make_model("openai-web", "gpt-5-4-standard")
    assert model.model_name == "openai-web:gpt-5-4-standard"


def test_system_property_openai():
    assert _make_model("openai-web", "gpt-5-3").system == "openai-web"


def test_system_property_google():
    assert _make_model("google-web", "gemini-3-flash").system == "google-web"


# ---------------------------------------------------------------------------
# request() — text response
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_request_returns_text_part():
    model = _make_model()
    model._client = _mock_client({"response": "Hello from the model!", "error": ""})
    messages = [ModelRequest(parts=[UserPromptPart(content="Hi")])]

    response = await model.request(messages, None, _request_params())

    assert len(response.parts) == 1
    assert isinstance(response.parts[0], TextPart)
    assert response.parts[0].content == "Hello from the model!"


@pytest.mark.asyncio
async def test_request_model_name_on_response():
    model = _make_model("google-web", "gemini-3-flash")
    model._client = _mock_client({"response": "ok", "error": ""})
    messages = [ModelRequest(parts=[UserPromptPart(content="Hi")])]

    response = await model.request(messages, None, _request_params())

    assert response.model_name == "google-web:gemini-3-flash"


@pytest.mark.asyncio
async def test_request_usage_estimated():
    prompt = "Hello world"
    reply = "This is a reply"
    model = _make_model()
    model._client = _mock_client({"response": reply, "error": ""})
    messages = [ModelRequest(parts=[UserPromptPart(content=prompt)])]

    response = await model.request(messages, None, _request_params())

    assert response.usage.input_tokens > 0
    assert response.usage.output_tokens > 0


@pytest.mark.asyncio
async def test_request_workflow_error_raises():
    model = _make_model()
    model._client = _mock_client({"error": "LLM backend unavailable", "response": ""})
    messages = [ModelRequest(parts=[UserPromptPart(content="Hi")])]

    with pytest.raises(WorkflowExecutionError, match="LLM backend unavailable"):
        await model.request(messages, None, _request_params())


@pytest.mark.asyncio
async def test_request_workflow_error_stores_workflow_id():
    model = _make_model()
    model._client = _mock_client({"error": "timeout", "response": ""})
    messages = [ModelRequest(parts=[UserPromptPart(content="Hi")])]

    with pytest.raises(WorkflowExecutionError) as exc_info:
        await model.request(messages, None, _request_params())

    assert exc_info.value.workflow_id is not None
    assert exc_info.value.workflow_id.startswith("llm-")


@pytest.mark.asyncio
async def test_request_execute_workflow_exception_wrapped():
    model = _make_model()
    client = MagicMock()
    client.execute_workflow = AsyncMock(side_effect=RuntimeError("network error"))
    model._client = client
    messages = [ModelRequest(parts=[UserPromptPart(content="Hi")])]

    with pytest.raises(WorkflowExecutionError, match="network error"):
        await model.request(messages, None, _request_params())


# ---------------------------------------------------------------------------
# request() — structured output
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_request_structured_output_returns_tool_call_part():
    model = _make_model()
    model._client = _mock_client({"response": '{"name": "Alice"}', "error": ""})

    output_tool = MagicMock()
    output_tool.name = "final_result"
    output_tool.parameters_json_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
    }

    messages = [ModelRequest(parts=[UserPromptPart(content="Who is it?")])]
    params = _request_params(output_tools=[output_tool])

    response = await model.request(messages, None, params)

    assert len(response.parts) == 1
    assert isinstance(response.parts[0], ToolCallPart)
    assert response.parts[0].tool_name == "final_result"


@pytest.mark.asyncio
async def test_request_structured_output_passes_json_instruction():
    """The workflow should receive a prompt with the JSON schema instruction appended."""
    model = _make_model()
    captured_args = {}

    async def fake_execute(workflow_name, payload, *, id, task_queue):
        captured_args.update(payload)
        return {"response": '{"x": 1}', "error": ""}

    client = MagicMock()
    client.execute_workflow = fake_execute
    model._client = client

    output_tool = MagicMock()
    output_tool.name = "result"
    output_tool.parameters_json_schema = {"type": "object"}

    messages = [ModelRequest(parts=[UserPromptPart(content="Compute")])]
    await model.request(messages, None, _request_params(output_tools=[output_tool]))

    assert "JSON Schema" in captured_args["prompt"]


# ---------------------------------------------------------------------------
# _get_temporal_client — caching
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_client_cached_after_first_call():
    model = _make_model()
    mock = MagicMock()
    model._client = mock

    c1 = await model._get_temporal_client()
    c2 = await model._get_temporal_client()

    assert c1 is c2 is mock

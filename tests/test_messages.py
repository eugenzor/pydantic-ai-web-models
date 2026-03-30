from datetime import datetime, timezone

from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    ToolReturnPart,
    UserPromptPart,
)

from pydantic_ai_web_models.messages import _extract_user_text, format_messages

_NOW = datetime.now(timezone.utc)


def _response(*parts):
    return ModelResponse(parts=list(parts), model_name="test-model", timestamp=_NOW)


# ---------------------------------------------------------------------------
# format_messages
# ---------------------------------------------------------------------------


def test_single_user_message_no_system():
    messages = [ModelRequest(parts=[UserPromptPart(content="Hello!")])]
    result = format_messages(messages)
    assert result == "Hello!"


def test_single_user_message_with_system_prompt():
    messages = [
        ModelRequest(
            parts=[
                SystemPromptPart(content="Be concise"),
                UserPromptPart(content="Hello!"),
            ]
        )
    ]
    result = format_messages(messages)
    assert "**System Instructions:**" in result
    assert "Be concise" in result
    assert "Hello!" in result


def test_multiple_system_parts_joined():
    messages = [
        ModelRequest(
            parts=[
                SystemPromptPart(content="Rule one"),
                SystemPromptPart(content="Rule two"),
                UserPromptPart(content="Go"),
            ]
        )
    ]
    result = format_messages(messages)
    assert "Rule one" in result
    assert "Rule two" in result


def test_instructions_parameter_included():
    messages = [ModelRequest(parts=[UserPromptPart(content="Test")])]
    result = format_messages(messages, instructions="Always respond in French")
    assert "Always respond in French" in result


def test_multi_turn_uses_prefixed_format():
    messages = [
        ModelRequest(parts=[UserPromptPart(content="Hi")]),
        _response(TextPart(content="Hello there!")),
        ModelRequest(parts=[UserPromptPart(content="How are you?")]),
    ]
    result = format_messages(messages)
    assert "User: Hi" in result
    assert "Assistant: Hello there!" in result
    assert "User: How are you?" in result


def test_multi_turn_with_system_prompt():
    messages = [
        ModelRequest(
            parts=[
                SystemPromptPart(content="Be brief"),
                UserPromptPart(content="Hi"),
            ]
        ),
        _response(TextPart(content="Hey!")),
        ModelRequest(parts=[UserPromptPart(content="Bye")]),
    ]
    result = format_messages(messages)
    assert "**System Instructions:**" in result
    assert "Be brief" in result
    assert "User: Hi" in result
    assert "Assistant: Hey!" in result
    assert "User: Bye" in result


def test_tool_return_appears_in_multi_turn():
    messages = [
        ModelRequest(
            parts=[
                UserPromptPart(content="Run the tool"),
                ToolReturnPart(
                    tool_name="my_tool",
                    content="tool output here",
                    tool_call_id="call-001",
                ),
            ]
        ),
        _response(TextPart(content="Done")),
        ModelRequest(parts=[UserPromptPart(content="Thanks")]),
    ]
    result = format_messages(messages)
    assert "Tool result (my_tool): tool output here" in result


def test_empty_messages_returns_empty_string():
    result = format_messages([])
    assert result == ""


def test_single_user_message_no_prefix():
    """The simple case should NOT add 'User:' prefix."""
    messages = [ModelRequest(parts=[UserPromptPart(content="Plain message")])]
    result = format_messages(messages)
    assert result == "Plain message"
    assert "User:" not in result


# ---------------------------------------------------------------------------
# _extract_user_text
# ---------------------------------------------------------------------------


def test_extract_user_text_string_content():
    part = UserPromptPart(content="hello world")
    assert _extract_user_text(part) == "hello world"


def test_extract_user_text_list_of_strings():
    part = UserPromptPart(content=["hello", "world"])
    assert _extract_user_text(part) == "hello world"


def test_extract_user_text_empty_list():
    part = UserPromptPart(content=[])
    assert _extract_user_text(part) == ""

import json
from unittest.mock import MagicMock

import pytest

from pydantic_ai_web_models.exceptions import JSONParseError
from pydantic_ai_web_models.structured import (
    build_json_schema_instruction,
    extract_json_from_response,
    wrap_as_tool_call,
)


# ---------------------------------------------------------------------------
# build_json_schema_instruction
# ---------------------------------------------------------------------------


def _make_tool(schema: dict) -> MagicMock:
    tool = MagicMock()
    tool.parameters_json_schema = schema
    return tool


def test_build_json_schema_instruction_contains_schema():
    schema = {"type": "object", "properties": {"name": {"type": "string"}}}
    result = build_json_schema_instruction(_make_tool(schema))
    assert '"type": "object"' in result
    assert '"name"' in result


def test_build_json_schema_instruction_contains_directive():
    schema = {"type": "object"}
    result = build_json_schema_instruction(_make_tool(schema))
    assert "Respond with ONLY valid JSON" in result
    assert "JSON Schema" in result


def test_build_json_schema_instruction_is_string():
    result = build_json_schema_instruction(_make_tool({"type": "object"}))
    assert isinstance(result, str)
    assert len(result) > 0


# ---------------------------------------------------------------------------
# extract_json_from_response
# ---------------------------------------------------------------------------


def test_extract_json_direct_parse():
    result = extract_json_from_response('{"key": "value", "num": 42}')
    assert result == {"key": "value", "num": 42}


def test_extract_json_with_whitespace():
    result = extract_json_from_response('  \n{"x": 1}\n  ')
    assert result == {"x": 1}


def test_extract_json_markdown_fence_json():
    result = extract_json_from_response('```json\n{"answer": "yes"}\n```')
    assert result == {"answer": "yes"}


def test_extract_json_markdown_fence_no_lang():
    result = extract_json_from_response('```\n{"answer": "yes"}\n```')
    assert result == {"answer": "yes"}


def test_extract_json_surrounding_text():
    result = extract_json_from_response('Here is the result: {"status": "ok"} end.')
    assert result == {"status": "ok"}


def test_extract_json_nested_object():
    data = {"outer": {"inner": [1, 2, 3]}}
    result = extract_json_from_response(json.dumps(data))
    assert result == data


def test_extract_json_invalid_raises_json_parse_error():
    with pytest.raises(JSONParseError) as exc_info:
        extract_json_from_response("not json at all")
    assert exc_info.value.raw_text == "not json at all"


def test_extract_json_array_raises_json_parse_error():
    # A bare JSON array is not a dict — should fail
    with pytest.raises(JSONParseError):
        extract_json_from_response("[1, 2, 3]")


def test_extract_json_empty_string_raises():
    with pytest.raises(JSONParseError):
        extract_json_from_response("")


def test_extract_json_error_message_mentions_length():
    raw = "garbage text here"
    with pytest.raises(JSONParseError, match=str(len(raw))):
        extract_json_from_response(raw)


# ---------------------------------------------------------------------------
# wrap_as_tool_call
# ---------------------------------------------------------------------------


def test_wrap_as_tool_call_tool_name():
    part = wrap_as_tool_call("output_tool", {"field": "data"})
    assert part.tool_name == "output_tool"


def test_wrap_as_tool_call_args():
    data = {"answer": 42, "reason": "computed"}
    part = wrap_as_tool_call("my_tool", data)
    assert part.args == data


def test_wrap_as_tool_call_id_format():
    part = wrap_as_tool_call("tool", {"x": 1})
    assert part.tool_call_id.startswith("call_")


def test_wrap_as_tool_call_unique_ids():
    p1 = wrap_as_tool_call("tool", {})
    p2 = wrap_as_tool_call("tool", {})
    assert p1.tool_call_id != p2.tool_call_id

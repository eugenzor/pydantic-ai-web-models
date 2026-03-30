"""Structured output: JSON schema instructions and response parsing."""

from __future__ import annotations

import json
import re
import uuid
from typing import Any

from pydantic_ai.messages import ToolCallPart

from .exceptions import JSONParseError


def build_json_schema_instruction(output_tool: Any) -> str:
    """Build a prompt instruction asking the model to respond in JSON.

    Args:
        output_tool: A ToolDefinition with ``parameters_json_schema``.

    Returns:
        Instruction text to append to the prompt.
    """
    schema = output_tool.parameters_json_schema
    schema_str = json.dumps(schema, indent=2)
    return (
        "\n\n---\n"
        "Respond with ONLY valid JSON matching this schema. "
        "Do not include any other text, explanation, or markdown code fences.\n\n"
        f"JSON Schema:\n```json\n{schema_str}\n```\n\n"
        "Your response must be a single JSON object matching the schema above."
    )


def extract_json_from_response(text: str) -> dict[str, Any]:
    """Extract and parse JSON from model response text.

    Tries multiple strategies:
    1. Direct parse of stripped text
    2. Strip markdown code fences and parse
    3. Find outermost ``{...}`` and parse

    Args:
        text: Raw model response text.

    Returns:
        Parsed JSON dict.

    Raises:
        JSONParseError: If no valid JSON can be extracted.
    """
    stripped = text.strip()

    # Strategy 1: direct parse
    try:
        result = json.loads(stripped)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # Strategy 2: strip markdown code fences
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", stripped, re.DOTALL)
    if fence_match:
        try:
            result = json.loads(fence_match.group(1).strip())
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

    # Strategy 3: find outermost { ... }
    brace_start = stripped.find("{")
    brace_end = stripped.rfind("}")
    if brace_start != -1 and brace_end > brace_start:
        try:
            result = json.loads(stripped[brace_start : brace_end + 1])
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

    raise JSONParseError(
        f"Could not extract valid JSON from response ({len(text)} chars)",
        raw_text=text,
    )


def wrap_as_tool_call(tool_name: str, parsed_json: dict[str, Any]) -> ToolCallPart:
    """Wrap parsed JSON as a ToolCallPart for pydantic-ai structured output.

    Args:
        tool_name: Name of the output tool.
        parsed_json: The parsed JSON data.

    Returns:
        A ToolCallPart that pydantic-ai will validate against the output schema.
    """
    return ToolCallPart(
        tool_name=tool_name,
        args=parsed_json,
        tool_call_id=f"call_{uuid.uuid4().hex[:16]}",
    )

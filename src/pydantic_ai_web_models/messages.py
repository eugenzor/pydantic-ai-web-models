"""Message formatting: flatten pydantic-ai messages into a single text prompt."""

from __future__ import annotations

import logging

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    ToolReturnPart,
    UserPromptPart,
)

logger = logging.getLogger(__name__)


def format_messages(
    messages: list[ModelMessage],
    instructions: str | None = None,
) -> str:
    """Convert pydantic-ai messages into a single text prompt.

    Args:
        messages: List of pydantic-ai ModelMessage objects.
        instructions: Optional system instructions to prepend.

    Returns:
        A formatted prompt string.
    """
    system_parts: list[str] = []
    user_texts: list[str] = []
    assistant_texts: list[str] = []
    conversation_parts: list[str] = []

    if instructions:
        system_parts.append(instructions)

    for msg in messages:
        if isinstance(msg, ModelRequest):
            for part in msg.parts:
                if isinstance(part, SystemPromptPart):
                    system_parts.append(part.content)
                elif isinstance(part, UserPromptPart):
                    text = _extract_user_text(part)
                    if text:
                        user_texts.append(text)
                        conversation_parts.append(f"User: {text}")
                elif isinstance(part, ToolReturnPart):
                    conversation_parts.append(
                        f"Tool result ({part.tool_name}): {part.content}"
                    )
        elif isinstance(msg, ModelResponse):
            for part in msg.parts:
                if isinstance(part, TextPart):
                    assistant_texts.append(part.content)
                    conversation_parts.append(f"Assistant: {part.content}")

    is_single_user_message = len(user_texts) == 1 and not assistant_texts

    if is_single_user_message:
        # Simple case: system prompt (if any) + single user message, no prefixes
        sections: list[str] = []
        if system_parts:
            system_prompt = "\n\n".join(system_parts)
            sections.append(f"**System Instructions:**\n{system_prompt}\n---")
        sections.append(user_texts[0])
        return "\n".join(sections)

    # Multi-turn conversation: use prefixed format
    sections = []
    if system_parts:
        system_prompt = "\n\n".join(system_parts)
        sections.append(f"**System Instructions:**\n{system_prompt}\n---")
    if conversation_parts:
        sections.append("\n".join(conversation_parts))

    return "\n\n".join(sections)


def _extract_user_text(part: UserPromptPart) -> str:
    """Extract text content from a UserPromptPart, skipping binary."""
    if isinstance(part.content, str):
        return part.content

    text_parts: list[str] = []
    for item in part.content:
        if isinstance(item, str):
            text_parts.append(item)
    return " ".join(text_parts)

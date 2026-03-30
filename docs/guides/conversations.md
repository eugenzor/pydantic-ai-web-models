---
icon: lucide/messages-square
---

# Conversations

`pydantic-ai-web-models` supports multi-turn conversations. Each call to `agent.run()` or
`agent.run_sync()` can carry the history of previous exchanges so the LLM has context for its
next reply.

## How Multi-Turn Works

After each `agent.run()` call, call `.all_messages()` on the result to get the full list of
messages for that conversation (both the user messages and the assistant replies). Pass this
list as `message_history=` to the next `agent.run()` call:

```python
result1 = await agent.run("First question")
result2 = await agent.run(
    "Follow-up question",
    message_history=result1.all_messages(),  # (1)!
)
```

1. `result1.all_messages()` returns a list of `ModelMessage` objects covering both the user
   turn and the assistant turn from the first call. Passing it to the second call gives the
   LLM full context.

## Full Async Example

```python title="conversations.py"
import asyncio
from pydantic_ai import Agent
import pydantic_ai_web_models


async def main():
    agent = Agent(model="google-web:gemini-3.1-pro")

    # First turn
    result1 = await agent.run("What are the three laws of thermodynamics?")
    print("Assistant:", result1.data)
    print()

    # Follow-up — the agent now has context from the first exchange
    result2 = await agent.run(
        "Can you explain the second one in simpler terms?",
        message_history=result1.all_messages(),
    )
    print("Assistant:", result2.data)


asyncio.run(main())
```

## Message Formatting

When the library forwards a conversation to the Temporal workflow it formats the messages as a
single text prompt. The format depends on how many turns are present:

- **Single message (no history)** — the prompt is sent as-is, with no speaker prefix:
  ```
  What is the capital of France?
  ```

- **Multi-turn conversation** — each turn is prefixed with `User:` or `Assistant:`:
  ```
  User: What are the three laws of thermodynamics?
  Assistant: The three laws are...
  User: Can you explain the second one in simpler terms?
  ```

- **System prompts** — if the agent has one or more system prompts, they are prepended to the
  formatted prompt as:
  ```
  **System Instructions:**
  You are a helpful assistant.
  ---
  User: ...
  ```

!!! note "Conversation length and token limits"
    Very long conversations will produce large prompts. The library approximates token usage as
    `len(text) // 4` (see [Architecture](../architecture.md#token-counting)), but the actual
    limit is determined by the web-based LLM's context window. If a conversation grows too long
    the workflow may return an error or a truncated response. Consider summarising older turns
    before passing them as history.

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

## Server-side thread (`thread_id`)

If your Temporal worker returns conversation handles (for example `LLMInvokeWorkflow` → `LLMInvokeResult` with `response`, `thread_id`, and `error`), you can **continue the chat in the browser** by passing **`thread_id`** on the next run. The new user text goes in `prompt` only; you do **not** need `message_history` on the agent if the worker session holds prior turns.

Use pydantic-ai’s **`model_settings`** (merged into the dict passed to the model each request). Read the handle from **`result.response.metadata`** — not from **`result.metadata`**, which is only for [`Agent.run(..., metadata=...)`](https://ai.pydantic.dev).

```python
result1 = await agent.run("First question")
tid = result1.response.metadata["thread_id"]

result2 = await agent.run(
    "Follow-up",
    model_settings={"thread_id": tid, "skip_system_prompt": True},
)
```

```python
result = agent.run_sync("What is the last human mission to the Moon?")
tid = result.response.metadata["thread_id"]
```

On **success**, workers following that contract set `error` to `""` and return a `thread_id`; `WebModel` copies it onto the assistant [`ModelResponse`](https://ai.pydantic.dev/api/messages/#pydantic_ai.messages.ModelResponse) as `metadata["thread_id"]`. On **failure** (non-empty `error` in the workflow result), `WebModel` raises **[`WorkflowExecutionError`](../api/exceptions.md)** — you do not get an assistant response to read `thread_id` from. Catch that and **[`TemporalConnectionError`](../api/exceptions.md)** like any other agent error.

- **`thread_id`** — forwarded to the workflow input when it is a non-empty string (whitespace is stripped).
- **`skip_system_prompt`** — when `True`, system instructions are omitted from the prompt sent to Temporal; use when the web session already has the system context.

For runs that produce **several** model replies in one agent step, you can still inspect [`result.new_messages()`](https://ai.pydantic.dev/api/agent/#pydantic_ai.agent.AgentRunResult) / `all_messages()`.

Static type checkers may not know about `thread_id` / `skip_system_prompt` on `ModelSettings`; they are passed at runtime. Use `typing.cast` or a small `TypedDict` if you want stricter typing.

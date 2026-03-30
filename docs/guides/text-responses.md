---
icon: lucide/message-square
---

# Text Responses

The simplest use case: send a prompt and receive a plain-text answer. This guide covers both
async and sync usage, system prompts, and notes on content that is not supported.

## Async Example

```python title="async_example.py"
import asyncio
from pydantic_ai import Agent
import pydantic_ai_web_models

async def main():
    agent = Agent(model="google-web:gemini-3-flash")
    result = await agent.run("Explain quantum computing in one paragraph.")
    print(result.data)

asyncio.run(main())
```

## Sync Example

```python title="sync_example.py"
from pydantic_ai import Agent
import pydantic_ai_web_models

agent = Agent(model="openai-web:gpt-5-3")
result = agent.run_sync("Write a haiku about Python programming.")
print(result.data)
```

## System Prompts

### Single System Prompt

Pass a static system prompt as a string directly to `Agent`:

```python title="system_prompt_string.py"
from pydantic_ai import Agent
import pydantic_ai_web_models

agent = Agent(
    model="google-web:gemini-3-flash",
    system_prompt="You are a helpful cooking assistant. Keep answers concise.",
)
result = agent.run_sync("How do I make scrambled eggs?")
print(result.data)
```

### Multiple System Prompts with Decorators

For more complex setups you can compose several system prompt functions using the
`@agent.system_prompt` decorator. Each decorated function returns a string; all strings are
concatenated (in registration order) before the user prompt.

```python title="system_prompt_decorators.py"
from pydantic_ai import Agent
import pydantic_ai_web_models

agent = Agent(model="openai-web:gpt-5-3")


@agent.system_prompt
def base_prompt() -> str:
    return "You are a travel guide specializing in European destinations."


@agent.system_prompt
def style_prompt() -> str:
    return "Always include a practical tip at the end of your response."


result = agent.run_sync("What should I see in Prague?")
print(result.data)
```

!!! note "Binary content is silently skipped"
    If any message in the conversation contains binary content — such as an image or file
    attachment — that part of the message is silently ignored. Only the text portions are
    forwarded to the Temporal workflow. This means agents that rely on vision or document
    understanding will not work correctly with this provider; use a native API-based provider
    for those cases.

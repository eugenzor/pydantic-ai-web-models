---
icon: lucide/home
---

# pydantic-ai-web-models

[![PyPI](https://img.shields.io/pypi/v/pydantic-ai-web-models)](https://pypi.org/project/pydantic-ai-web-models/)
[![Python](https://img.shields.io/pypi/pyversions/pydantic-ai-web-models)](https://pypi.org/project/pydantic-ai-web-models/)

!!! danger "Educational project — read before using"
    This project was created for **personal learning and educational purposes only**. It is not
    intended for production use, nor does it encourage or endorse circumventing any terms of
    service. The author makes no warranties and accepts no liability for any misuse. Users are
    solely responsible for ensuring their usage complies with the terms of service of OpenAI,
    Google, and any other third-party services they interact with.

A lightweight [Pydantic AI](https://ai.pydantic.dev/) model provider that routes requests to
web-based LLMs through [Temporal](https://temporal.io/) workflows. The Temporal worker handles
browser-based LLM access on your behalf — **no LLM API keys are required in your application**.

!!! warning "This package does not include Temporal workflows"
    `pydantic-ai-web-models` provides **only the Pydantic AI model provider** — the client that
    sends requests to Temporal. It does **not** ship the Temporal workflows needed to execute LLM
    requests against web-based models. You must build and deploy your own Temporal worker that
    implements the `LLMInvokeWorkflow` workflow type. Without a running worker, this package
    **cannot work on its own**.

## Features

- [x] Drop-in provider strings — use `"google-web:gemini-3-flash"` or `"openai-web:gpt-5-3"` directly in `Agent(model=...)`
- [x] No LLM API keys needed in your application code
- [x] Pydantic structured output — pass `output_type=MyModel` and get validated, typed responses
- [x] Multi-turn conversations via `message_history=result.all_messages()`
- [x] Temporal Cloud and mTLS authentication supported
- [x] Fully environment-driven configuration via `.env` file or env vars
- [x] Python 3.11+

## Quick Example

```python title="quick_start.py" hl_lines="3 6 7"
from pydantic_ai import Agent
import pydantic_ai_web_models  # (1)!

agent = Agent(model="google-web:gemini-3-flash")  # (2)!

result = agent.run_sync("What is the capital of France?")  # (3)!
print(result.data)
# Paris is the capital of France...
```

1. Importing the package automatically registers `google-web` and `openai-web` providers with Pydantic AI. No explicit setup call is needed.
2. Pass a provider-prefixed model string directly to `Agent`. Both `"google-web:..."` and `"openai-web:..."` are supported.
3. Use `run_sync` for synchronous code or `await agent.run(...)` in async contexts.

!!! tip "Ready to dive in?"
    Head over to [Getting Started](getting-started.md) for installation instructions, environment
    setup, and your first working agent in under five minutes.

## Available Models

| Provider | Model String | Description |
|---|---|---|
| `google-web` | `google-web:gemini-3-flash` | Gemini 3 Flash — fast, general-purpose |
| `google-web` | `google-web:gemini-3-flash-thinking` | Gemini 3 Flash with extended reasoning |
| `google-web` | `google-web:gemini-3.1-pro` | Gemini 3.1 Pro — highest capability Google model |
| `openai-web` | `openai-web:gpt-5-3` | GPT-5-3 — fast OpenAI model |
| `openai-web` | `openai-web:gpt-5-4-standard` | GPT-5-4 Standard — balanced OpenAI model |
| `openai-web` | `openai-web:gpt-5-4-extended` | GPT-5-4 Extended — maximum capability OpenAI model |

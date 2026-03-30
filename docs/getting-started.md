---
icon: lucide/rocket
---

# Getting Started

This page walks you through installing `pydantic-ai-web-models`, configuring your environment,
and running your first agent against a web-based LLM via Temporal.

!!! warning "Temporal workflows are not included"
    This package is a **client-only** Pydantic AI provider. It does not include the Temporal
    workflows required to execute LLM requests. You must develop and deploy your own Temporal
    worker that implements `LLMInvokeWorkflow`. The package cannot function without it.

## Prerequisites

Before you begin, make sure you have the following in place:

- **Temporal server** — a running instance at `localhost:7233` (local dev) or a Temporal Cloud namespace.
- **Temporal worker** — a worker process listening on the `ai-worker-task-queue` task queue that
  implements the `LLMInvokeWorkflow` workflow type. This worker is responsible for invoking the
  actual web-based LLM on your behalf.
- **Python 3.11+** — the package requires Python 3.11 or later.

!!! info "What is the Temporal worker?"
    The Temporal worker (`ai-worker-task-queue` / `LLMInvokeWorkflow`) is a separate process that
    holds browser-based sessions with Google and OpenAI. Your application code never calls LLM APIs
    directly — it sends a workflow execution request to Temporal, and the worker handles the rest.
    See [Architecture](architecture.md) for the full request flow.

## Installation

=== "uv"

    ```bash
    uv add pydantic-ai-web-models
    ```

=== "pip"

    ```bash
    pip install pydantic-ai-web-models
    ```

The package declares `pydantic-ai` and `temporalio` as dependencies, so they will be installed
automatically.

## Environment Setup

All connection parameters are read from environment variables (or a `.env` file in the working
directory). Copy the provided example file and edit it for your environment:

```bash
cp .env.example .env
```

For a local Temporal server the minimal configuration is:

```env title=".env"
TEMPORAL_ADDRESS=localhost:7233
TEMPORAL_NAMESPACE=default
```

The task queue and workflow name default to `ai-worker-task-queue` and `LLMInvokeWorkflow`
respectively, so you only need to override them if your worker uses different names.

!!! note "Code-based configuration"
    Configuration can also be set entirely in Python using `set_default_config`. See the
    [Configuration](configuration.md) page for all options, including Temporal Cloud API keys
    and mTLS certificate authentication.

## Quick Start

=== "Async"

    ```python title="async_example.py"
    import asyncio
    from pydantic_ai import Agent
    import pydantic_ai_web_models  # registers providers on import

    async def main():
        agent = Agent(model="google-web:gemini-3-flash")
        result = await agent.run("Explain quantum computing in one paragraph.")
        print(result.data)

    asyncio.run(main())
    ```

=== "Sync"

    ```python title="sync_example.py"
    from pydantic_ai import Agent
    import pydantic_ai_web_models  # registers providers on import

    agent = Agent(model="openai-web:gpt-5-3")
    result = agent.run_sync("Write a haiku about Python programming.")
    print(result.data)
    ```

!!! tip "Provider registration"
    The `import pydantic_ai_web_models` line is what registers the `google-web` and `openai-web`
    provider prefixes with Pydantic AI. Without this import, passing those model strings to `Agent`
    will raise an `UnknownModelError`. You do not need to call any additional setup function —
    the import is sufficient.

## Next Steps

Now that you have a working agent, explore the rest of the documentation:

- **[Configuration](configuration.md)** — detailed reference for all environment variables,
  Temporal Cloud setup, mTLS certificates, and code-based config.
- **[Guides](guides/index.md)** — practical examples for text responses, structured output,
  multi-turn conversations, and comparing models side-by-side.
- **[API Reference](api/index.md)** — full interface documentation for `WebModel`,
  `TemporalConfig`, and all exceptions.
- **[Architecture](architecture.md)** — a detailed look at the request flow, message formatting,
  and the structured output pipeline.

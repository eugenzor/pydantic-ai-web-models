# pydantic_ai_web_models

[![PyPI](https://img.shields.io/pypi/v/pydantic-ai-web-models)](https://pypi.org/project/pydantic-ai-web-models/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://pypi.org/project/pydantic-ai-web-models/)
[![Docs](https://img.shields.io/badge/docs-eugenzor.github.io-blue)](https://eugenzor.github.io/pydantic-ai-web-models/)

> **Disclaimer:** This project was created for **personal learning and educational purposes only**. It is not intended for production use, nor does it encourage or endorse circumventing any terms of service. The author makes no warranties and accepts no liability for any misuse. Users are solely responsible for ensuring their usage complies with the terms of service of OpenAI, Google, and any other third-party services they interact with.

A lightweight [Pydantic AI](https://ai.pydantic.dev/) model provider that routes requests to web-based LLMs (OpenAI, Google) through [Temporal](https://temporal.io/) workflows. No API keys needed — the Temporal worker handles browser-based LLM access.

**Documentation:** https://eugenzor.github.io/pydantic-ai-web-models/

> **Important:** This package provides **only the Pydantic AI model provider** (the client side). It does **not** include the Temporal workflows required to actually execute LLM requests. You must develop and deploy your own Temporal worker that implements the `LLMInvokeWorkflow` workflow type. Without a running worker that handles browser-based LLM access, this package cannot function on its own.

## Installation

```bash
pip install pydantic-ai-web-models
```

or with uv:

```bash
uv add pydantic-ai-web-models
```

## Prerequisites

- A running Temporal server (default: `localhost:7233`)
- A Temporal worker listening on `ai-worker-task-queue` that implements the `LLMInvokeWorkflow`
- Python 3.11+
- `pydantic-ai` and `temporalio` installed

## Quick Start

```python
from pydantic_ai import Agent
import pydantic_ai_web_models  # registers providers on import

agent = Agent(model="google-web:gemini-3-flash")
result = agent.run_sync("What is the capital of France?")
print(result.data)
# Paris is the capital of France...
```

Importing `pydantic_ai_web_models` automatically registers the `openai-web` and `google-web` prefixes with Pydantic AI's model inference, so you can pass model strings directly to `Agent()`.

## Available Models

| Provider      | Model String                          | Description                    |
|---------------|---------------------------------------|--------------------------------|
| `google-web`  | `google-web:gemini-3-flash`           | Gemini 3 Flash                 |
| `google-web`  | `google-web:gemini-3-flash-thinking`  | Gemini 3 Flash with thinking   |
| `google-web`  | `google-web:gemini-3.1-pro`           | Gemini 3.1 Pro                 |
| `openai-web`  | `openai-web:gpt-5-3`                  | GPT-5-3                        |
| `openai-web`  | `openai-web:gpt-5-4-standard`        | GPT-5-4 Standard               |
| `openai-web`  | `openai-web:gpt-5-4-extended`        | GPT-5-4 Extended               |

## Usage Examples

### Basic Text Response (Async)

```python
import asyncio
from pydantic_ai import Agent
import pydantic_ai_web_models

async def main():
    agent = Agent(model="google-web:gemini-3-flash")
    result = await agent.run("Explain quantum computing in one paragraph.")
    print(result.data)

asyncio.run(main())
```

### Basic Text Response (Sync)

```python
from pydantic_ai import Agent
import pydantic_ai_web_models

agent = Agent(model="openai-web:gpt-5-3")
result = agent.run_sync("Write a haiku about Python programming.")
print(result.data)
```

### Structured Output

Use Pydantic models as `output_type` to get validated, typed responses. The model is instructed to respond with JSON matching the schema, and the response is automatically parsed and validated.

```python
from pydantic import BaseModel
from pydantic_ai import Agent
import pydantic_ai_web_models


class CityInfo(BaseModel):
    name: str
    country: str
    population: int
    famous_for: list[str]


agent = Agent(
    model="google-web:gemini-3-flash",
    output_type=CityInfo,
)
result = agent.run_sync("Tell me about Tokyo.")
city = result.data

print(f"{city.name}, {city.country}")
print(f"Population: {city.population:,}")
print(f"Famous for: {', '.join(city.famous_for)}")
# Tokyo, Japan
# Population: 13,960,000
# Famous for: cherry blossoms, Shibuya crossing, sushi, anime
```

### Structured Output with Nested Models

```python
from pydantic import BaseModel
from pydantic_ai import Agent
import pydantic_ai_web_models


class Address(BaseModel):
    street: str
    city: str
    country: str


class Person(BaseModel):
    name: str
    age: int
    occupation: str
    address: Address


agent = Agent(
    model="openai-web:gpt-5-4-standard",
    output_type=Person,
)
result = agent.run_sync(
    "Generate a fictional person living in Berlin who works as a software engineer."
)
person = result.data

print(f"{person.name}, age {person.age}")
print(f"Works as: {person.occupation}")
print(f"Lives at: {person.address.street}, {person.address.city}")
```

### System Prompts

```python
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

```python
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

### Multi-turn Conversations

```python
import asyncio
from pydantic_ai import Agent
import pydantic_ai_web_models


async def main():
    agent = Agent(model="google-web:gemini-3.1-pro")

    # First turn
    result1 = await agent.run("What are the three laws of thermodynamics?")
    print(result1.data)

    # Follow-up using message history
    result2 = await agent.run(
        "Can you explain the second one in simpler terms?",
        message_history=result1.all_messages(),
    )
    print(result2.data)


asyncio.run(main())
```

### Structured Output with Enums and Optional Fields

```python
from enum import Enum
from pydantic import BaseModel
from pydantic_ai import Agent
import pydantic_ai_web_models


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ReviewAnalysis(BaseModel):
    sentiment: Sentiment
    confidence: float
    key_topics: list[str]
    summary: str
    improvement_suggestion: str | None = None


agent = Agent(
    model="openai-web:gpt-5-4-standard",
    output_type=ReviewAnalysis,
)
result = agent.run_sync(
    "Analyze this review: 'The food was amazing but the service was incredibly slow. "
    "We waited 45 minutes for our appetizers. The dessert almost made up for it though.'"
)
analysis = result.data

print(f"Sentiment: {analysis.sentiment.value} ({analysis.confidence:.0%})")
print(f"Topics: {', '.join(analysis.key_topics)}")
print(f"Summary: {analysis.summary}")
if analysis.improvement_suggestion:
    print(f"Suggestion: {analysis.improvement_suggestion}")
```

### Comparing Models Side-by-Side

```python
import asyncio
from pydantic_ai import Agent
import pydantic_ai_web_models

MODELS = [
    "google-web:gemini-3-flash",
    "openai-web:gpt-5-3",
]


async def ask_model(model: str, prompt: str) -> str:
    agent = Agent(model=model)
    result = await agent.run(prompt)
    return result.data


async def main():
    prompt = "In exactly one sentence, what is the meaning of life?"
    tasks = [ask_model(m, prompt) for m in MODELS]
    responses = await asyncio.gather(*tasks)

    for model, response in zip(MODELS, responses):
        print(f"[{model}]: {response}\n")


asyncio.run(main())
```

## Configuration

### Via Environment Variables

All connection parameters can be set through environment variables (or a `.env` file in the working directory). Copy `.env.example` to `.env` and fill in the values relevant to your setup.

#### Local / self-hosted Temporal

```env
TEMPORAL_ADDRESS=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=ai-worker-task-queue
TEMPORAL_TIMEOUT_SECONDS=300
```

#### Temporal Cloud — API key authentication

Generate an API key in the Temporal Cloud UI under **Settings → API Keys**, then:

```env
TEMPORAL_ADDRESS=<namespace>.tmprl.cloud:7233
TEMPORAL_NAMESPACE=<namespace>.<account-id>
TEMPORAL_API_KEY=<your-api-key>
TEMPORAL_TASK_QUEUE=ai-worker-task-queue
```

`TEMPORAL_ADDRESS` and `TEMPORAL_NAMESPACE` are read by the Temporal SDK's `envconfig` bridge; `TEMPORAL_API_KEY` is also consumed there and configures bearer-token auth automatically — no additional code is required.

#### mTLS client certificates

For self-hosted clusters that require mutual TLS, provide paths to PEM-encoded files:

```env
TEMPORAL_ADDRESS=temporal.internal:7233
TEMPORAL_NAMESPACE=production
TEMPORAL_TLS_CERT=/path/to/client.pem
TEMPORAL_TLS_KEY=/path/to/client.key
# Optional — only needed for a custom/private CA:
TEMPORAL_TLS_CA=/path/to/ca.pem
# Optional — override TLS server name (SNI):
TEMPORAL_TLS_SERVER_NAME=temporal.internal
TEMPORAL_TASK_QUEUE=ai-worker-task-queue
```

`TEMPORAL_TLS_CERT` / `TEMPORAL_TLS_KEY` / `TEMPORAL_TLS_CA` / `TEMPORAL_TLS_SERVER_NAME` are **not** handled by the SDK bridge; they are read by `TemporalConfig` (via pydantic-settings) and applied when building the `TLSConfig` object before connecting.

> **Note:** `TEMPORAL_API_KEY` and mTLS are mutually exclusive. Use one or the other depending on your cluster's auth policy.

#### Full environment variable reference

| Variable                    | Default                  | Handled by          | Description                                          |
|-----------------------------|--------------------------|---------------------|------------------------------------------------------|
| `TEMPORAL_ADDRESS`          | `localhost:7233`         | SDK `envconfig`     | Temporal server address (`host:port`)                |
| `TEMPORAL_NAMESPACE`        | `default`                | SDK `envconfig`     | Temporal namespace                                   |
| `TEMPORAL_API_KEY`          | *(unset)*                | SDK `envconfig`     | Bearer token for Temporal Cloud API key auth         |
| `TEMPORAL_TLS_CERT`         | *(unset)*                | `TemporalConfig`    | Path to PEM client certificate (mTLS)                |
| `TEMPORAL_TLS_KEY`          | *(unset)*                | `TemporalConfig`    | Path to PEM client private key (mTLS)                |
| `TEMPORAL_TLS_CA`           | *(unset)*                | `TemporalConfig`    | Path to PEM CA certificate (mTLS, optional)          |
| `TEMPORAL_TLS_SERVER_NAME`  | *(unset)*                | `TemporalConfig`    | Override TLS SNI hostname (mTLS, optional)           |
| `TEMPORAL_TASK_QUEUE`       | `ai-worker-task-queue`   | `TemporalConfig`    | Task queue the worker listens on                     |
| `TEMPORAL_WORKFLOW_NAME`    | `LLMInvokeWorkflow`      | `TemporalConfig`    | Workflow type name registered on the worker          |
| `TEMPORAL_TIMEOUT_SECONDS`  | `300`                    | `TemporalConfig`    | Workflow execution timeout in seconds                |

### Custom Temporal Connection

By default, the package connects to `localhost:7233`. Override this before creating any agents:

```python
from pydantic_ai_web_models import set_default_config, TemporalConfig

set_default_config(TemporalConfig(
    host="temporal.internal:7233",
    namespace="production",
    task_queue="llm-workers",
    timeout_seconds=600,
))
```

### Per-Model Temporal Config

Pass a config directly when constructing a model:

```python
from pydantic_ai import Agent
from pydantic_ai_web_models import WebModel, TemporalConfig

model = WebModel(
    provider="google-web",
    model_name="gemini-3.1-pro",
    temporal_config=TemporalConfig(
        host="remote-temporal:7233",
        task_queue="gpu-workers",
    ),
)
agent = Agent(model=model)
result = agent.run_sync("Hello!")
```

### TemporalConfig Fields

| Field             | Type  | Default                  | Description                          |
|-------------------|-------|--------------------------|--------------------------------------|
| `host`            | `str` | `"localhost:7233"`       | Temporal server address              |
| `namespace`       | `str` | `"default"`              | Temporal namespace                   |
| `task_queue`      | `str` | `"ai-worker-task-queue"` | Task queue the worker listens on     |
| `workflow_name`   | `str` | `"LLMInvokeWorkflow"`   | Name of the workflow to execute      |
| `timeout_seconds` | `int` | `300`                    | Workflow execution timeout (seconds) |

## Error Handling

```python
from pydantic_ai import Agent
from pydantic_ai_web_models import (
    TemporalConnectionError,
    WorkflowExecutionError,
    JSONParseError,
)
import pydantic_ai_web_models

agent = Agent(model="google-web:gemini-3-flash")

try:
    result = agent.run_sync("Hello!")
    print(result.data)
except TemporalConnectionError as e:
    print(f"Cannot reach Temporal server: {e}")
except WorkflowExecutionError as e:
    print(f"LLM workflow failed (id={e.workflow_id}): {e}")
except JSONParseError as e:
    # Only happens with structured output
    print(f"Failed to parse JSON: {e}")
    print(f"Raw response was: {e.raw_text[:200]}")
```

## Architecture

```
Agent.run() / Agent.run_sync()
    |
    v
WebModel.request()
    |
    +-- format_messages()        # flatten messages to text prompt
    +-- build_json_schema_instruction()  # (structured output only)
    |
    v
Temporal LLMInvokeWorkflow
    |
    +-- prompt + model string sent to Temporal worker
    +-- worker invokes web LLM (OpenAI/Google web interface)
    +-- response text returned
    |
    v
WebModel.request()
    |
    +-- extract_json_from_response()  # (structured output only)
    +-- wrap_as_tool_call()           # (structured output only)
    |
    v
ModelResponse (returned to pydantic-ai)
```

## Limitations

- **No streaming** — responses are returned in full after the workflow completes
- **No tool/function calls** — only text and structured output are supported
- **No binary content** — images and files in messages are skipped
- **Estimated token counts** — usage is approximated as `len(text) // 4` since the workflow API does not return token counts
- **Requires Temporal infrastructure** — a running Temporal server and worker are needed

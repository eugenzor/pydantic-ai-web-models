---
icon: lucide/cpu
---

# WebModel

`WebModel` is the core class of `pydantic-ai-web-models`. It implements the pydantic-ai `Model`
interface and routes every inference request through a Temporal workflow to a web-based LLM.

## Constructor

```python
class WebModel:
    def __init__(
        self,
        provider: str,
        model_name: str,
        *,
        temporal_config: TemporalConfig | None = None,
    ) -> None: ...
```

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `provider` | `str` | Yes | Provider identifier. Must be one of `"google-web"` or `"openai-web"`. |
| `model_name` | `str` | Yes | Model name within the provider. Must be a key in `AVAILABLE_MODELS[provider]`. |
| `temporal_config` | `TemporalConfig \| None` | No | Temporal connection configuration. If `None`, the module-level default (see `get_default_config`) is used. |

### Raises

- `ValueError` — if `provider` is not a recognised provider string.
- `ValueError` — if `model_name` is not listed under the given `provider` in `AVAILABLE_MODELS`.

## Properties

| Property | Type | Description |
|---|---|---|
| `model_name` | `str` | The full model identifier in `"provider:model_name"` format, e.g. `"google-web:gemini-3-flash"`. |
| `system` | `str` | The provider string, e.g. `"google-web"`. |

## Usage

```python title="web_model_direct.py"
from pydantic_ai import Agent
from pydantic_ai_web_models import WebModel, TemporalConfig

# Construct a WebModel explicitly instead of using a model string
model = WebModel(
    provider="google-web",
    model_name="gemini-3.1-pro",
    temporal_config=TemporalConfig(
        task_queue="gpu-workers",
        timeout_seconds=900,
    ),
)

agent = Agent(model=model)
result = agent.run_sync("Summarise the history of the internet.")
print(result.data)
```

## Temporal Client Lifecycle

The Temporal client is created **lazily** on the first request and is cached for the lifetime
of the `WebModel` instance. Subsequent requests from the same `WebModel` reuse the same client
without reconnecting.

!!! note "Thread safety"
    Client creation is protected by an `asyncio.Lock`. If multiple coroutines call a `WebModel`
    concurrently before the client has been initialised, only one will perform the connection;
    the others will wait and then reuse the client once it is ready. The lock is per-instance,
    so different `WebModel` objects create their clients independently.

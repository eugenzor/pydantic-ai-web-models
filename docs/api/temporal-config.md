---
icon: lucide/sliders
---

# TemporalConfig

`TemporalConfig` is a pydantic-settings `BaseSettings` subclass that holds the Temporal
connection parameters managed by this library. It reads its values from environment variables
or a `.env` file using the `TEMPORAL_` prefix.

## Class Definition

```python
from pydantic_ai_web_models import TemporalConfig

config = TemporalConfig()           # reads from env / .env
config = TemporalConfig(            # explicit values
    task_queue="my-queue",
    timeout_seconds=600,
)
```

## Fields Reference

| Field | Type | Default | Env Var | Description |
|---|---|---|---|---|
| `task_queue` | `str` | `"ai-worker-task-queue"` | `TEMPORAL_TASK_QUEUE` | Task queue the Temporal worker listens on. Must match the queue your worker is registered with. |
| `workflow_name` | `str` | `"LLMInvokeWorkflow"` | `TEMPORAL_WORKFLOW_NAME` | Workflow type name registered on the worker. Change only if your worker uses a different name. |
| `timeout_seconds` | `int` | `300` | `TEMPORAL_TIMEOUT_SECONDS` | Maximum time (in seconds) to wait for the workflow to complete before raising a timeout error. |
| `tls_cert` | `Path \| None` | `None` | `TEMPORAL_TLS_CERT` | Path to a PEM-encoded client certificate file (mTLS). |
| `tls_key` | `Path \| None` | `None` | `TEMPORAL_TLS_KEY` | Path to a PEM-encoded client private key file (mTLS). |
| `tls_ca` | `Path \| None` | `None` | `TEMPORAL_TLS_CA` | Path to a PEM-encoded CA certificate file (mTLS, optional). Only needed for private/custom CAs. |
| `tls_server_name` | `str \| None` | `None` | `TEMPORAL_TLS_SERVER_NAME` | Override the TLS SNI hostname (mTLS, optional). Useful when the server's TLS certificate does not match its hostname. |

!!! info "SDK-managed variables"
    Three important connection variables — `TEMPORAL_ADDRESS`, `TEMPORAL_NAMESPACE`, and
    `TEMPORAL_API_KEY` — are **not** fields of `TemporalConfig`. They are handled directly by
    the Temporal Python SDK's `envconfig` bridge when the client is created. You do not need to
    pass them to `TemporalConfig`; simply set them in the environment and the SDK will pick them
    up automatically.

## `get_default_config`

```python
def get_default_config() -> TemporalConfig: ...
```

Returns the current module-level `TemporalConfig` instance. This is the configuration that will
be used by any `WebModel` that does not have an explicit `temporal_config` argument.

The first call to `get_default_config()` (or the first time a `WebModel` is created without an
explicit config) constructs a `TemporalConfig()` by reading the environment. Subsequent calls
return the same cached instance unless `set_default_config` has been called in the meantime.

## `set_default_config`

```python
def set_default_config(config: TemporalConfig) -> None: ...
```

Replaces the module-level default `TemporalConfig`. All `WebModel` instances created **after**
this call will use the new configuration. Instances that were created before the call are not
affected (they have already captured a reference to the old config).

```python title="set_default_config_example.py"
from pydantic_ai_web_models import set_default_config, TemporalConfig

set_default_config(TemporalConfig(
    task_queue="production-llm-workers",
    timeout_seconds=600,
))
```

## `AVAILABLE_MODELS`

```python
AVAILABLE_MODELS: dict[str, list[str]]
```

A dictionary mapping each supported provider name to the list of model names available under
that provider:

```python
AVAILABLE_MODELS = {
    "google-web": [
        "gemini-3-flash",
        "gemini-3-flash-thinking",
        "gemini-3.1-pro",
    ],
    "openai-web": [
        "gpt-5-3",
        "gpt-5-4-standard",
        "gpt-5-4-extended",
    ],
}
```

When constructing a `WebModel` directly, both the `provider` argument and the `model_name`
argument are validated against this dictionary. Passing an unknown provider or model name raises
a `ValueError`.

When using a model string with `Agent(model="provider:model_name")`, the same validation is
performed during provider inference.

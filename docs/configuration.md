---
icon: lucide/settings
---

# Configuration

`pydantic-ai-web-models` is configured through environment variables, a `.env` file in the
working directory, or directly in Python code. The most common approach is to use a `.env` file
for credentials and connection details, keeping them out of your source code.

## Environment Variables

The table below covers all supported variables. The sections that follow show which subset you
need for each connection scenario.

### Connection Scenarios

=== "Local / self-hosted"

    For a locally running Temporal server (the default), only the address and namespace need to
    be set — and even those are optional if you are using the defaults:

    ```env title=".env"
    TEMPORAL_ADDRESS=localhost:7233
    TEMPORAL_NAMESPACE=default
    TEMPORAL_TASK_QUEUE=ai-worker-task-queue
    TEMPORAL_TIMEOUT_SECONDS=300
    ```

    The `TEMPORAL_ADDRESS` and `TEMPORAL_NAMESPACE` defaults are `localhost:7233` and `default`,
    so this entire block can be omitted for a plain local setup.

=== "Temporal Cloud (API key)"

    Generate an API key in the Temporal Cloud UI under **Settings → API Keys**, then configure:

    ```env title=".env"
    TEMPORAL_ADDRESS=<namespace>.tmprl.cloud:7233
    TEMPORAL_NAMESPACE=<namespace>.<account-id>
    TEMPORAL_API_KEY=<your-api-key>
    TEMPORAL_TASK_QUEUE=ai-worker-task-queue
    ```

    Replace `<namespace>`, `<account-id>`, and `<your-api-key>` with the values from your
    Temporal Cloud account. `TEMPORAL_ADDRESS` and `TEMPORAL_NAMESPACE` are read by the Temporal
    SDK's `envconfig` bridge; `TEMPORAL_API_KEY` is also consumed there and enables bearer-token
    authentication automatically — no additional code is required.

=== "mTLS certificates"

    For clusters that require mutual TLS, provide paths to PEM-encoded certificate files:

    ```env title=".env"
    TEMPORAL_ADDRESS=temporal.internal:7233
    TEMPORAL_NAMESPACE=production
    TEMPORAL_TLS_CERT=/path/to/client.pem
    TEMPORAL_TLS_KEY=/path/to/client.key
    # Optional — only needed for a private/custom CA:
    TEMPORAL_TLS_CA=/path/to/ca.pem
    # Optional — override TLS SNI hostname:
    TEMPORAL_TLS_SERVER_NAME=temporal.internal
    TEMPORAL_TASK_QUEUE=ai-worker-task-queue
    ```

    The four `TEMPORAL_TLS_*` variables are **not** handled by the Temporal SDK bridge. They are
    read by `TemporalConfig` (via pydantic-settings) and are applied when building the `TLSConfig`
    object before establishing the connection.

!!! warning "API key and mTLS are mutually exclusive"
    Do not set `TEMPORAL_API_KEY` and `TEMPORAL_TLS_CERT`/`TEMPORAL_TLS_KEY` at the same time.
    Use the authentication method that matches your cluster's security policy. Mixing the two will
    cause a connection error.

### Full Variable Reference

| Variable | Default | Handled by | Description |
|---|---|---|---|
| `TEMPORAL_ADDRESS` | `localhost:7233` | SDK `envconfig` | Temporal server address (`host:port`) |
| `TEMPORAL_NAMESPACE` | `default` | SDK `envconfig` | Temporal namespace |
| `TEMPORAL_API_KEY` | *(unset)* | SDK `envconfig` | Bearer token for Temporal Cloud API key auth |
| `TEMPORAL_TLS_CERT` | *(unset)* | `TemporalConfig` | Path to PEM client certificate (mTLS) |
| `TEMPORAL_TLS_KEY` | *(unset)* | `TemporalConfig` | Path to PEM client private key (mTLS) |
| `TEMPORAL_TLS_CA` | *(unset)* | `TemporalConfig` | Path to PEM CA certificate (mTLS, optional) |
| `TEMPORAL_TLS_SERVER_NAME` | *(unset)* | `TemporalConfig` | Override TLS SNI hostname (mTLS, optional) |
| `TEMPORAL_TASK_QUEUE` | `ai-worker-task-queue` | `TemporalConfig` | Task queue the worker listens on |
| `TEMPORAL_WORKFLOW_NAME` | `LLMInvokeWorkflow` | `TemporalConfig` | Workflow type name registered on the worker |
| `TEMPORAL_TIMEOUT_SECONDS` | `300` | `TemporalConfig` | Workflow execution timeout in seconds |

!!! info "`.env` file loading"
    pydantic-settings loads `.env` automatically from the **current working directory** when your
    application starts. If you run your script from a different directory, make sure the `.env`
    file is in the directory from which you invoke Python (or set the variables in the shell
    environment instead).

## Code-Based Configuration

Environment variables are convenient, but you can also configure the library entirely in Python.
This is useful for tests, programmatic setups, or when you want to keep all configuration in one
place.

### Setting the Module-Level Default

Call `set_default_config` before creating any agents. All subsequently created `WebModel`
instances (including those created implicitly by `Agent(model="google-web:...")`) will use this
configuration.

```python title="configure_default.py" hl_lines="4 5 6 7 8"
from pydantic_ai_web_models import set_default_config, TemporalConfig

# Override the module-level default before creating any agents
set_default_config(TemporalConfig(
    task_queue="llm-workers",
    workflow_name="LLMInvokeWorkflow",
    timeout_seconds=600,
))

# All agents created after this call will use the config above
from pydantic_ai import Agent
import pydantic_ai_web_models

agent = Agent(model="google-web:gemini-3-flash")
result = agent.run_sync("Hello!")
print(result.data)
```

### Per-Model Configuration

Pass a `TemporalConfig` directly to `WebModel` to override the default for a single model
instance. This is useful when you need different timeout values or task queues for different
agents in the same process.

```python title="per_model_config.py" hl_lines="5 6 7 8 9 10"
from pydantic_ai import Agent
from pydantic_ai_web_models import WebModel, TemporalConfig

# This model connects to a different task queue with a longer timeout
model = WebModel(
    provider="google-web",
    model_name="gemini-3.1-pro",
    temporal_config=TemporalConfig(
        task_queue="gpu-workers",
        timeout_seconds=900,
    ),
)

agent = Agent(model=model)
result = agent.run_sync("Write a detailed analysis of the Roman Empire.")
print(result.data)
```

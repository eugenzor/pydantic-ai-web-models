---
icon: lucide/alert-triangle
---

# Exceptions

All exceptions raised by `pydantic-ai-web-models` inherit from `WebModelError`, making it easy
to catch all library errors with a single `except` clause when needed.

## Exception Hierarchy

```
Exception
└── WebModelError
    ├── TemporalConnectionError
    ├── WorkflowExecutionError
    ├── ModelLimitReachedError
    └── JSONParseError
```

## `WebModelError`

```python
class WebModelError(Exception): ...
```

Base class for all exceptions raised by this library. Catch `WebModelError` to handle any error
from `pydantic-ai-web-models` in a single clause, or catch the specific subclasses for more
targeted error handling.

## `TemporalConnectionError`

```python
class TemporalConnectionError(WebModelError): ...
```

Raised when the library cannot establish a connection to the Temporal server. Common causes
include:

- The Temporal server is not running at the configured address.
- Network or firewall rules are blocking the connection.
- Incorrect `TEMPORAL_ADDRESS` or `TEMPORAL_NAMESPACE` values.
- Invalid or expired `TEMPORAL_API_KEY`.
- TLS certificate mismatch or missing mTLS credentials.

## `WorkflowExecutionError`

```python
class WorkflowExecutionError(WebModelError):
    workflow_id: str | None
```

Raised when the Temporal workflow starts successfully but returns an error during execution.
This can happen when:

- The LLM returns an error or is unavailable on the worker side.
- The workflow times out (exceeds `timeout_seconds`).
- The worker raises an application-level error.

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `workflow_id` | `str \| None` | The Temporal workflow ID of the failed execution. Use this to look up the workflow in the Temporal UI or CLI for debugging. May be `None` if the workflow ID was not available at the time of the error. |

## `ModelLimitReachedError`

```python
class ModelLimitReachedError(WebModelError):
    suggestion: str | None
    model_name: str | None
    workflow_id: str | None
```

Raised when the upstream LLM provider reports that the model's quota or limit has been
reached. The Temporal worker signals this condition by raising:

```python
from temporalio import exceptions

raise exceptions.ApplicationError(
    "Model limit is reached",
    "Try another model",
    type="LIMIT_REACHED",
    non_retryable=True,
)
```

The library translates that workflow failure into `ModelLimitReachedError` so callers can
react in plain Python -- typically by switching to a different model -- without depending
on Temporal exception types.

The error is non-retryable: retrying with the same model will hit the same limit. Catch it
and fall back to another configured model.

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `suggestion` | `str \| None` | Human-readable hint from the worker (the first detail of the `ApplicationError`, e.g. `"Try another model"`). |
| `model_name` | `str \| None` | The fully-qualified model that hit the limit (e.g. `"openai-web:gpt-5-5"`). |
| `workflow_id` | `str \| None` | The Temporal workflow ID of the failed execution. |

### Handling Example

```python title="fallback_on_limit.py"
from pydantic_ai import Agent
from pydantic_ai_web_models import ModelLimitReachedError
import pydantic_ai_web_models  # noqa: F401  -- registers providers

primary = Agent(model="openai-web:gpt-5-5")
fallback = Agent(model="google-web:gemini-3-flash")

try:
    result = primary.run_sync("Summarize the latest release notes.")
except ModelLimitReachedError as exc:
    print(f"{exc.model_name} hit its limit: {exc} ({exc.suggestion})")
    result = fallback.run_sync("Summarize the latest release notes.")

print(result.data)
```

## `JSONParseError`

```python
class JSONParseError(WebModelError):
    raw_text: str
```

Raised when structured output is requested (i.e., `output_type` is set on the `Agent`) but the
library cannot extract valid JSON from the LLM's response after exhausting all three parsing
strategies (direct parse, markdown fence stripping, and outermost-brace extraction).

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `raw_text` | `str` | The full raw text of the LLM response that could not be parsed. Inspect this to understand what the model actually returned. |

## Error Handling Example

```python title="error_handling.py" hl_lines="3 4 5 6 7 8 9"
from pydantic_ai import Agent
from pydantic_ai_web_models import (
    TemporalConnectionError,
    WorkflowExecutionError,
    ModelLimitReachedError,
    JSONParseError,
    WebModelError,
)
import pydantic_ai_web_models

agent = Agent(model="google-web:gemini-3-flash")

try:
    result = agent.run_sync("Hello!")
    print(result.data)
except TemporalConnectionError as e:
    # Server unreachable — check TEMPORAL_ADDRESS and network connectivity
    print(f"Cannot reach Temporal server: {e}")
except ModelLimitReachedError as e:
    # Quota exhausted — switch to another model rather than retry
    print(f"{e.model_name} is over its limit ({e.suggestion}); falling back...")
except WorkflowExecutionError as e:
    # Workflow started but failed — check Temporal UI for details
    print(f"LLM workflow failed (workflow_id={e.workflow_id}): {e}")
except JSONParseError as e:
    # Only raised for structured output — the model didn't return valid JSON
    print(f"Failed to parse JSON response: {e}")
    print(f"Raw response was:\n{e.raw_text[:500]}")
except WebModelError as e:
    # Catch-all for any other library error
    print(f"Unexpected library error: {e}")
```

---
icon: lucide/code
---

# API Reference

**Package:** `pydantic_ai_web_models`

This section documents all public exports of the package. Import them directly from the
top-level module:

```python
from pydantic_ai_web_models import (
    WebModel,
    TemporalConfig,
    get_default_config,
    set_default_config,
    AVAILABLE_MODELS,
    WebModelError,
    TemporalConnectionError,
    WorkflowExecutionError,
    JSONParseError,
)
```

## Public Exports

| Name | Kind | Description |
|---|---|---|
| [`WebModel`](web-model.md) | Class | The main model class. Implements the pydantic-ai `Model` interface and routes requests to Temporal. |
| [`TemporalConfig`](temporal-config.md) | Class | pydantic-settings `BaseSettings` subclass that holds all Temporal connection parameters. |
| [`get_default_config`](temporal-config.md#get_default_config) | Function | Returns the current module-level `TemporalConfig` instance. |
| [`set_default_config`](temporal-config.md#set_default_config) | Function | Replaces the module-level `TemporalConfig`. Takes effect for all subsequently created `WebModel` instances. |
| [`AVAILABLE_MODELS`](temporal-config.md#available_models) | Dict | Mapping of provider name to list of supported model name strings. |
| [`WebModelError`](exceptions.md#webmodelerror) | Exception | Base class for all exceptions raised by this library. |
| [`TemporalConnectionError`](exceptions.md#temporalconnectionerror) | Exception | Raised when the library cannot connect to the Temporal server. |
| [`WorkflowExecutionError`](exceptions.md#workflowexecutionerror) | Exception | Raised when the Temporal workflow returns an error. Carries `workflow_id`. |
| [`JSONParseError`](exceptions.md#jsonparseerror) | Exception | Raised when structured-output JSON extraction fails. Carries `raw_text`. |

## Auto-Registration

!!! info "Provider registration on import"
    Importing `pydantic_ai_web_models` automatically patches `pydantic_ai.models.infer_model`
    to recognise the `"google-web:"` and `"openai-web:"` provider prefixes. This means you can
    pass these model strings directly to `Agent(model=...)` without explicitly constructing a
    `WebModel` instance.

    The registration happens once at import time and is idempotent — importing the module
    multiple times is safe.

    ```python
    import pydantic_ai_web_models  # registration happens here

    from pydantic_ai import Agent
    agent = Agent(model="google-web:gemini-3-flash")  # just works
    ```

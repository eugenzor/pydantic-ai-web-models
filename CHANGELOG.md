# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-05-07

### Added

#### Error Handling

- **`ModelLimitReachedError`** — new exception raised when the upstream model reports that its quota or limit is reached. The Temporal worker signals this by raising `temporalio.exceptions.ApplicationError("Model limit is reached", "Try another model", type="LIMIT_REACHED", non_retryable=True)`; the library now translates that workflow failure into `ModelLimitReachedError` so callers can react in plain Python (typically by switching to a different model) without depending on Temporal exception types. Exposes `suggestion`, `model_name`, and `workflow_id` attributes.

### Fixed

#### Core

- `WebModel.request()` no longer raises `NameError` on workflow failures: the previous build referenced an unimported `WorkflowFailureError` in its except branch. The handler is now driven by a `_translate_limit_reached` helper that lazy-imports the Temporal types and falls back to wrapping unrelated failures as `WorkflowExecutionError` as before.


## [0.3.0] - 2026-05-05

### Changed

#### Models

- Replaced `openai-web:gpt-5-4-standard` and `openai-web:gpt-5-4-extended` with `openai-web:gpt-5-5` — the two GPT-5-4 variants are no longer available; `gpt-5-5` is their successor.


## [0.2.0] - 2026-04-04

### Added

#### Core

- **`thread_id` via `model_settings`** — optional non-empty string (whitespace stripped) included in the Temporal workflow payload so workers can continue a server-side browser/chat thread (e.g. `LLMInvokeWorkflow` input).
- **`skip_system_prompt` via `model_settings`** — when the value is exactly `True`, `format_messages()` omits the `**System Instructions:**` block and all `SystemPromptPart` content from the prompt string sent to Temporal; conversation turns are unchanged.
- **Workflow `thread_id` on success** — when the workflow result includes a non-empty `thread_id` string and `error` is empty, it is copied onto the assistant [`ModelResponse`](https://ai.pydantic.dev/api/messages/#pydantic_ai.messages.ModelResponse) as `metadata["thread_id"]`. Read it with `result.response.metadata["thread_id"]` from pydantic-ai’s [`AgentRunResult.response`](https://ai.pydantic.dev/api/agent/#pydantic_ai.agent.AgentRunResult). Non-empty `error` still raises `WorkflowExecutionError`.


## [0.1.0] - 2026-04-01

### Added

#### Core

- `WebModel` — Pydantic AI `Model` implementation that routes inference requests through a Temporal workflow to web-based LLMs. Accepts `provider`, `model_name`, and an optional `temporal_config`.
- Auto-registration of `google-web` and `openai-web` provider prefixes with Pydantic AI on package import — no explicit setup call required.
- Six built-in model identifiers:
  - `google-web:gemini-3-flash`
  - `google-web:gemini-3-flash-thinking`
  - `google-web:gemini-3.1-pro`
  - `openai-web:gpt-5-3`
  - `openai-web:gpt-5-4-standard`
  - `openai-web:gpt-5-4-extended`
- Lazy Temporal client creation on first request, cached per `WebModel` instance and protected by `asyncio.Lock` for safe concurrent access.

#### Configuration

- `TemporalConfig` — Pydantic Settings model for Temporal connection parameters (`host`, `namespace`, `task_queue`, `workflow_name`, `timeout_seconds`).
- `set_default_config` / `get_default_config` — module-level helpers to share a single `TemporalConfig` across all `WebModel` instances.
- Full environment variable support via a `.env` file or shell environment: `TEMPORAL_ADDRESS`, `TEMPORAL_NAMESPACE`, `TEMPORAL_TASK_QUEUE`, `TEMPORAL_WORKFLOW_NAME`, `TEMPORAL_TIMEOUT_SECONDS`.
- Temporal Cloud API key authentication via `TEMPORAL_API_KEY` (consumed by the Temporal SDK `envconfig` bridge).
- mTLS client certificate authentication via `TEMPORAL_TLS_CERT`, `TEMPORAL_TLS_KEY`, `TEMPORAL_TLS_CA`, and `TEMPORAL_TLS_SERVER_NAME`.

#### Inference Features

- Plain text responses — supports both `agent.run_sync()` (sync) and `await agent.run()` (async).
- Structured output — pass `output_type=MyPydanticModel` to receive a validated, typed response. The model is prompted with the JSON schema and the response is parsed automatically using a three-strategy extraction pipeline (direct parse → markdown fence stripping → outermost-brace extraction).
- Multi-turn conversations — pass `message_history=result.all_messages()` to maintain context across turns.
- System prompt support — single and multiple system prompts (including decorator-based `@agent.system_prompt`) are concatenated and prepended to the formatted prompt.
- Message formatting — converts pydantic-ai `ModelMessage` lists to a single text prompt with `User:` / `Assistant:` prefixes for multi-turn history and a `**System Instructions:**` header for system prompts. Binary content parts (images, files) are silently skipped.
- Approximate token counting — usage reported via `result.usage()` is estimated as `len(text) // 4` since the Temporal workflow API does not return token counts.

#### Error Handling

- `WebModelError` — base exception for all library errors.
- `TemporalConnectionError` — raised when the Temporal server cannot be reached.
- `WorkflowExecutionError` — raised when the workflow starts but fails during execution; exposes `workflow_id` for Temporal UI lookup.
- `JSONParseError` — raised when structured output parsing fails after all three extraction strategies are exhausted; exposes `raw_text` for inspection.

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

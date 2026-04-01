# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

#### Documentation

- Full MkDocs site with Getting Started, Configuration, Guides (text responses, structured output, conversations, model comparison), API Reference (`WebModel`, `TemporalConfig`, exceptions), and Architecture pages.
- Architecture diagram showing the full request flow from `Agent.run()` through Temporal to the web LLM and back.

[0.1.0]: https://github.com/eugeneagi/pydantic-ai-web-models/releases/tag/v0.1.0

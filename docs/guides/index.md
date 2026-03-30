---
icon: lucide/book-open
---

# Guides

The guides in this section provide practical, task-oriented examples for common use cases. Each
guide focuses on a single topic and includes working code that you can copy and adapt directly.

All examples assume you have already installed the package and have a Temporal server and worker
running. See [Getting Started](../getting-started.md) if you have not done that yet.

## Available Guides

### [Text Responses](text-responses.md)

Learn how to get plain-text answers from web-based LLMs. Covers async and sync usage, single
system prompts, multiple system prompts with the `@agent.system_prompt` decorator, and notes on
binary content handling.

### [Structured Output](structured-output.md)

Use Pydantic models as `output_type` to get validated, typed responses. Covers basic models,
nested models, enums, optional fields, and how the JSON extraction pipeline works internally.

### [Conversations](conversations.md)

Build multi-turn conversations by passing `message_history` between calls. Includes a full async
two-turn example and details on how messages are formatted for the Temporal workflow.

### [Comparing Models](comparing-models.md)

Run the same prompt against multiple models concurrently using `asyncio.gather`. Useful for
benchmarking response quality or latency across providers.

---

For a complete reference of all classes, functions, and exceptions, see the
[API Reference](../api/index.md).

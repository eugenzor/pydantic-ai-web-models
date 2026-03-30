"""WebModel: pydantic-ai Model backed by Temporal LLM workflows."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from uuid import uuid4

from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart
from pydantic_ai.models import Model, ModelRequestParameters
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import RequestUsage

from .config import AVAILABLE_MODELS, TemporalConfig, get_default_config
from .exceptions import TemporalConnectionError, WorkflowExecutionError
from .messages import format_messages
from .structured import (
    build_json_schema_instruction,
    extract_json_from_response,
    wrap_as_tool_call,
)

logger = logging.getLogger(__name__)


class WebModel(Model):
    """Pydantic AI model using Temporal workflows to invoke web LLMs.

    Supports ``openai-web`` and ``google-web`` providers.  Does not support
    tool calls or streaming -- only single-request text and structured output.

    Examples:
        >>> from pydantic_ai import Agent
        >>> import pydantic_ai_web_models  # auto-registers providers
        >>> agent = Agent(model="google-web:gemini-3-flash")
        >>> result = await agent.run("Hello!")
    """

    def __init__(
        self,
        provider: str,
        model_name: str,
        *,
        temporal_config: TemporalConfig | None = None,
    ):
        self._provider = provider
        self._model_name_short = model_name
        self._temporal_config = temporal_config or get_default_config()
        self._client: object | None = None
        self._client_lock: asyncio.Lock | None = None

        if provider not in AVAILABLE_MODELS:
            raise ValueError(
                f"Unknown provider: {provider!r}. Available: {list(AVAILABLE_MODELS)}"
            )
        if model_name not in AVAILABLE_MODELS[provider]:
            raise ValueError(
                f"Unknown model {model_name!r} for provider {provider!r}. "
                f"Available: {AVAILABLE_MODELS[provider]}"
            )

        logger.debug(
            "Initialized WebModel: provider=%s, model=%s",
            provider,
            model_name,
        )

    @property
    def model_name(self) -> str:
        return f"{self._provider}:{self._model_name_short}"

    @property
    def system(self) -> str:
        return self._provider

    async def _get_temporal_client(self) -> object:
        """Get or create a cached Temporal client.

        Base connection parameters (address, namespace) come from the SDK's
        ``temporalio.envconfig``.  TLS certificate paths are read via
        pydantic-settings because the SDK bridge does not pick them up from
        environment variables.
        """
        if self._client_lock is None:
            self._client_lock = asyncio.Lock()

        async with self._client_lock:
            if self._client is not None:
                return self._client

            try:
                from temporalio.client import Client
                from temporalio.envconfig import ClientConfig
                from temporalio.service import TLSConfig

                connect_config = ClientConfig.load_client_connect_config()

                cfg = self._temporal_config
                if cfg.tls_cert and cfg.tls_key:
                    connect_config["tls"] = TLSConfig(
                        client_cert=cfg.tls_cert.read_bytes(),
                        client_private_key=cfg.tls_key.read_bytes(),
                        server_root_ca_cert=(
                            cfg.tls_ca.read_bytes() if cfg.tls_ca else None
                        ),
                        domain=cfg.tls_server_name,
                    )

                self._client = await Client.connect(**connect_config)
                return self._client
            except Exception as exc:
                raise TemporalConnectionError(
                    f"Failed to connect to Temporal: {exc}"
                ) from exc

    async def request(
        self,
        messages: list[ModelMessage],
        model_settings: ModelSettings | None,
        model_request_parameters: ModelRequestParameters,
    ) -> ModelResponse:
        """Make a request via Temporal LLMInvokeWorkflow."""
        output_tools = model_request_parameters.output_tools

        # Build prompt
        prompt = format_messages(messages)
        if output_tools:
            prompt += build_json_schema_instruction(output_tools[0])

        # Execute workflow
        client = await self._get_temporal_client()
        workflow_id = f"llm-{uuid4()}"

        try:
            result = await client.execute_workflow(  # type: ignore[union-attr]
                self._temporal_config.workflow_name,
                {
                    "prompt": prompt,
                    "model": self.model_name,
                },
                id=workflow_id,
                task_queue=self._temporal_config.task_queue,
            )
        except Exception as exc:
            if isinstance(exc, (TemporalConnectionError, WorkflowExecutionError)):
                raise
            raise WorkflowExecutionError(
                f"Workflow execution failed: {exc}",
                workflow_id=workflow_id,
            ) from exc

        # Check for workflow-level error
        error = result.get("error", "")
        if error:
            raise WorkflowExecutionError(error, workflow_id=workflow_id)

        response_text = result.get("response", "")

        # Estimate token usage
        usage = RequestUsage(
            input_tokens=len(prompt) // 4,
            output_tokens=len(response_text) // 4,
        )

        # Parse response
        if output_tools:
            parsed = extract_json_from_response(response_text)
            tool_call = wrap_as_tool_call(output_tools[0].name, parsed)
            return ModelResponse(
                parts=[tool_call],
                model_name=self.model_name,
                timestamp=datetime.now(timezone.utc),
                usage=usage,
            )

        return ModelResponse(
            parts=[TextPart(content=response_text)],
            model_name=self.model_name,
            timestamp=datetime.now(timezone.utc),
            usage=usage,
        )

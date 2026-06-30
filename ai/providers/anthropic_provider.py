"""
Claude provider (anthropic SDK) — included as the OCP proof:
adding this file + the import in __init__ was the ONLY change needed to give
the debate a neutral third-party judge. DeepSeek/Grok follow the same template.
"""
from __future__ import annotations

import logging
from typing import Optional

from ai.providers.base import (
    LLMProvider, ProviderConfig, ProviderError, TransientProviderError,
)
from ai.providers.registry import register_provider

logger = logging.getLogger(__name__)


@register_provider
class AnthropicProvider(LLMProvider):
    name = "claude"
    requires_secret = "ANTHROPIC_API_KEY"
    default_model = "claude-3-5-sonnet-20241022"

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        from anthropic import Anthropic  # lazy optional dep
        self._client = Anthropic(api_key=config.api_key, timeout=config.timeout)

    def _raw_generate(self, system_instruction, user_prompt, temperature, max_tokens) -> str:
        try:
            from anthropic import (APITimeoutError, APIConnectionError,
                                   RateLimitError, InternalServerError)
            transient = (APITimeoutError, APIConnectionError, RateLimitError, InternalServerError)
        except Exception:  # pragma: no cover
            transient = tuple()
        try:
            msg = self._client.messages.create(
                model=self.config.model,
                system=system_instruction,
                max_tokens=max_tokens or self.config.max_output_tokens,
                temperature=self.config.temperature if temperature is None else temperature,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = "".join(
                getattr(b, "text", "") for b in msg.content
                if getattr(b, "type", "") == "text"
            ).strip()
            if not text:
                raise ProviderError("empty response")
            return text
        except ProviderError:
            raise
        except transient as exc:  # type: ignore[misc]
            raise TransientProviderError(str(exc)) from exc
        except Exception as exc:
            if any(m in str(exc).lower() for m in ("429", "timeout", "503", "502", "500", "overloaded", "rate")):
                raise TransientProviderError(str(exc)) from exc
            raise ProviderError(str(exc)) from exc

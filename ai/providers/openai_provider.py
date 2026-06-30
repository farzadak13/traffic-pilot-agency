"""OpenAI provider (openai>=1.x)."""
from __future__ import annotations

import logging
from typing import Optional

from ai.providers.base import (
    LLMProvider, ProviderConfig, ProviderError, TransientProviderError,
)
from ai.providers.registry import register_provider

logger = logging.getLogger(__name__)


@register_provider
class OpenAIProvider(LLMProvider):
    name = "openai"
    requires_secret = "OPENAI_API_KEY"
    default_model = "gpt-4o"

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        from openai import OpenAI  # lazy optional dep
        self._client = OpenAI(api_key=config.api_key, timeout=config.timeout)

    def _raw_generate(self, system_instruction, user_prompt, temperature, max_tokens) -> str:
        try:
            from openai import (APITimeoutError, APIConnectionError,
                                RateLimitError, InternalServerError)
            transient = (APITimeoutError, APIConnectionError, RateLimitError, InternalServerError)
        except Exception:  # pragma: no cover
            transient = tuple()
        try:
            resp = self._client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "system", "content": system_instruction},
                          {"role": "user", "content": user_prompt}],
                temperature=self.config.temperature if temperature is None else temperature,
                max_tokens=max_tokens or self.config.max_output_tokens,
            )
            text = (resp.choices[0].message.content or "").strip()
            if not text:
                raise ProviderError("empty response")
            return text
        except ProviderError:
            raise
        except transient as exc:  # type: ignore[misc]
            raise TransientProviderError(str(exc)) from exc
        except Exception as exc:
            if any(m in str(exc).lower() for m in ("429", "timeout", "503", "502", "500", "rate")):
                raise TransientProviderError(str(exc)) from exc
            raise ProviderError(str(exc)) from exc

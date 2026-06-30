"""Gemini provider (google-generativeai)."""
from __future__ import annotations

import logging
from typing import Optional

from ai.providers.base import (
    LLMProvider, ProviderConfig, ProviderError, TransientProviderError,
)
from ai.providers.registry import register_provider

logger = logging.getLogger(__name__)
_TRANSIENT = ("429", "500", "502", "503", "deadline", "timeout",
              "unavailable", "rate", "overload")


@register_provider
class GeminiProvider(LLMProvider):
    name = "gemini"
    requires_secret = "GEMINI_API_KEY"
    default_model = "gemini-2.5-flash"

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        import google.generativeai as genai  # lazy: optional dependency
        genai.configure(api_key=config.api_key)
        self._genai = genai

    def _raw_generate(self, system_instruction, user_prompt, temperature, max_tokens) -> str:
        genai = self._genai
        try:
            model = genai.GenerativeModel(self.config.model, system_instruction=system_instruction)
            response = model.generate_content(
                user_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature if temperature is None else temperature,
                    max_output_tokens=max_tokens or self.config.max_output_tokens,
                ),
                request_options={"timeout": self.config.timeout},
            )
            text = (getattr(response, "text", "") or "").strip()
            if not text:
                raise ProviderError("empty response (safety block / no candidates)")
            return text
        except ProviderError:
            raise
        except Exception as exc:
            if any(m in str(exc).lower() for m in _TRANSIENT):
                raise TransientProviderError(str(exc)) from exc
            raise ProviderError(str(exc)) from exc

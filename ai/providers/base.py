"""
Provider abstraction layer — async-first, vendor-agnostic.

SOLID:
- SRP : a provider only turns (system, prompt) -> text.
- DIP : the debate engine depends on `LLMProvider`, never on a vendor SDK
        or on `streamlit.secrets`.
- ISP : two narrow capabilities — `generate` (sync) and `agenerate` (async).
- OCP : new models are added by subclassing + `@register_provider`.

Every provider ships standardized Retry + Exponential Backoff (+jitter) +
Timeout + structured logging. `agenerate` offloads the blocking SDK call to a
worker thread (`asyncio.to_thread`) so the orchestrator can fan out truly
concurrently with `asyncio.gather`.
"""
from __future__ import annotations

import abc
import asyncio
import logging
import random
import time
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────
# Value objects
# ──────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class ProviderConfig:
    """Immutable config injected into a provider (no global state)."""
    api_key: str
    model: str
    temperature: float = 0.7
    max_output_tokens: int = 8192
    timeout: float = 60.0
    max_retries: int = 3
    backoff_base: float = 1.6   # seconds, exponential
    backoff_jitter: float = 0.3  # fraction of the computed backoff


@dataclass
class LLMResponse:
    """Normalized envelope returned by EVERY provider call."""
    provider: str
    model: str
    text: str
    role: str = "generate"          # draft | critique | judge — for observability
    ok: bool = True
    error: Optional[str] = None
    latency_ms: int = 0
    attempts: int = 1

    @property
    def is_usable(self) -> bool:
        return self.ok and bool(self.text and self.text.strip())


# ──────────────────────────────────────────────────────────────────────────
# Error taxonomy
# ──────────────────────────────────────────────────────────────────────────
class ProviderError(RuntimeError):
    """Non-retryable failure (bad key, blocked content, schema violation)."""


class TransientProviderError(ProviderError):
    """Retryable failure (timeout, 429 rate-limit, 5xx)."""


def _backoff_seconds(cfg: ProviderConfig, attempt: int) -> float:
    base = cfg.backoff_base ** attempt
    return base + random.uniform(0.0, cfg.backoff_jitter * base)


# ──────────────────────────────────────────────────────────────────────────
# Interface
# ──────────────────────────────────────────────────────────────────────────
class LLMProvider(abc.ABC):
    """Vendor-agnostic text generator.

    Subclasses MUST set the class attributes below so the registry can build
    them with zero orchestrator changes (OCP):
        name           — unique key, e.g. "gemini"
        requires_secret— secrets mapping key, e.g. "GEMINI_API_KEY"
        default_model  — model id used when no override is provided
    """

    name: str = "base"
    requires_secret: str = "API_KEY"
    default_model: str = ""

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config

    # vendor-specific call -------------------------------------------------
    @abc.abstractmethod
    def _raw_generate(
        self,
        system_instruction: str,
        user_prompt: str,
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> str:
        """Blocking vendor call. MUST raise (Transient)ProviderError on failure."""
        raise NotImplementedError

    # shared retry cores ---------------------------------------------------
    def _retry_sync(self, call: Callable[[], str]) -> Tuple[str, int]:
        last: Optional[Exception] = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                return call(), attempt
            except TransientProviderError as exc:
                last = exc
                sleep_s = _backoff_seconds(self.config, attempt)
                logger.warning("[%s] transient (%d/%d): %s — retry in %.1fs",
                               self.name, attempt, self.config.max_retries, exc, sleep_s)
                time.sleep(sleep_s)
            except ProviderError:
                raise
            except Exception as exc:  # noqa: BLE001
                last = exc
                logger.error("[%s] unexpected: %s", self.name, exc)
                break
        raise ProviderError(f"{self.name} failed after {self.config.max_retries} retries: {last}")

    async def _retry_async(self, call: Callable[[], str]) -> Tuple[str, int]:
        last: Optional[Exception] = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                text = await asyncio.to_thread(call)   # offload blocking SDK call
                return text, attempt
            except TransientProviderError as exc:
                last = exc
                sleep_s = _backoff_seconds(self.config, attempt)
                logger.warning("[%s] transient (%d/%d): %s — retry in %.1fs",
                               self.name, attempt, self.config.max_retries, exc, sleep_s)
                await asyncio.sleep(sleep_s)
            except ProviderError:
                raise
            except Exception as exc:  # noqa: BLE001
                last = exc
                logger.error("[%s] unexpected: %s", self.name, exc)
                break
        raise ProviderError(f"{self.name} failed after {self.config.max_retries} retries: {last}")

    # public API -----------------------------------------------------------
    def _envelope(self, fn, role, start, attempts=1, text="", err=None) -> LLMResponse:
        return LLMResponse(
            provider=self.name, model=self.config.model, text=text, role=role,
            ok=err is None, error=err, attempts=attempts,
            latency_ms=int((time.perf_counter() - start) * 1000),
        )

    def generate(self, system_instruction: str, user_prompt: str, *, role: str = "generate",
                 temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> LLMResponse:
        """Sync entry; never raises — failures return LLMResponse(ok=False)."""
        start = time.perf_counter()
        try:
            text, attempts = self._retry_sync(
                lambda: self._raw_generate(system_instruction, user_prompt, temperature, max_tokens))
            return self._envelope(None, role, start, attempts, text=text)
        except ProviderError as exc:
            return self._envelope(None, role, start, err=str(exc))

    async def agenerate(self, system_instruction: str, user_prompt: str, *, role: str = "generate",
                        temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> LLMResponse:
        """Async entry; never raises — failures return LLMResponse(ok=False)."""
        start = time.perf_counter()
        try:
            text, attempts = await self._retry_async(
                lambda: self._raw_generate(system_instruction, user_prompt, temperature, max_tokens))
            return self._envelope(None, role, start, attempts, text=text)
        except ProviderError as exc:
            return self._envelope(None, role, start, err=str(exc))

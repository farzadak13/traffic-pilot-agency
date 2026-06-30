"""
Provider registry / factory — Open/Closed via a registration decorator.

Add Claude / DeepSeek / Grok by creating a provider module that does:

    @register_provider
    class GrokProvider(LLMProvider):
        name = "grok"; requires_secret = "GROK_API_KEY"; default_model = "grok-2"
        ...

and importing it in `ai/providers/__init__.py`. The orchestrator NEVER changes.

DIP: `build_registry` accepts ANY Mapping (st.secrets, os.environ, a test dict),
so the AI layer does not import streamlit.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Mapping, Optional, Type

from ai.providers.base import LLMProvider, ProviderConfig

logger = logging.getLogger(__name__)

# populated by the @register_provider decorator
_PROVIDER_TYPES: Dict[str, Type[LLMProvider]] = {}


def register_provider(cls: Type[LLMProvider]) -> Type[LLMProvider]:
    """Class decorator: self-registers a provider under its `name`."""
    if not getattr(cls, "name", None) or cls.name == "base":
        raise ValueError(f"{cls.__name__} must define a unique `name`")
    _PROVIDER_TYPES[cls.name] = cls
    logger.debug("registered provider '%s' -> %s", cls.name, cls.__name__)
    return cls


def registered_providers() -> List[str]:
    return list(_PROVIDER_TYPES.keys())


class ProviderRegistry:
    """Holds the live, instantiated providers for one request/session."""

    def __init__(self) -> None:
        self._providers: Dict[str, LLMProvider] = {}

    def register(self, key: str, provider: LLMProvider) -> None:
        self._providers[key] = provider

    def get(self, key: str) -> LLMProvider:
        if key not in self._providers:
            raise KeyError(f"provider '{key}' is not registered")
        return self._providers[key]

    def available(self) -> List[str]:
        return list(self._providers.keys())


def build_registry(
    secrets: Mapping[str, str],
    model_overrides: Optional[Mapping[str, str]] = None,
    temperature: float = 0.7,
    only: Optional[List[str]] = None,
) -> ProviderRegistry:
    """Instantiate every registered provider whose secret is present.

    `only` optionally restricts which provider keys to build. Providers with a
    missing key are skipped (graceful degradation), never raised.
    """
    overrides = dict(model_overrides or {})
    registry = ProviderRegistry()
    keys = only or registered_providers()
    for key in keys:
        cls = _PROVIDER_TYPES.get(key)
        if cls is None:
            logger.warning("provider '%s' is not registered — skipped", key)
            continue
        api_key = secrets.get(cls.requires_secret)
        if not api_key:
            logger.warning("provider '%s' skipped — missing %s", key, cls.requires_secret)
            continue
        cfg = ProviderConfig(
            api_key=api_key,
            model=overrides.get(key, cls.default_model),
            temperature=temperature,
        )
        try:
            registry.register(key, cls(cfg))
        except Exception as exc:  # init failure must not kill the app
            logger.error("provider '%s' failed to init: %s", key, exc)
    return registry

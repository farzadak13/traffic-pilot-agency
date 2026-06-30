"""Importing this package auto-registers all bundled providers (OCP)."""
from ai.providers.base import (
    LLMProvider, LLMResponse, ProviderConfig,
    ProviderError, TransientProviderError,
)
from ai.providers.registry import (
    ProviderRegistry, build_registry, register_provider, registered_providers,
)

# side-effect imports -> @register_provider runs. Add new providers here.
from ai.providers import gemini_provider  # noqa: E402,F401
from ai.providers import openai_provider  # noqa: E402,F401
from ai.providers import anthropic_provider  # noqa: E402,F401

__all__ = [
    "LLMProvider", "LLMResponse", "ProviderConfig",
    "ProviderError", "TransientProviderError",
    "ProviderRegistry", "build_registry", "register_provider", "registered_providers",
]

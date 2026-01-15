"""
LLM Adapters Package

Contains adapters for various LLM providers, each implementing the BaseLLMAdapter interface.
"""

from typing import Type

from ..base import BaseLLMAdapter


# Adapter registry - maps provider_type to adapter class
_ADAPTER_REGISTRY: dict[str, Type[BaseLLMAdapter]] = {}


def register_adapter(provider_type: str):
    """Decorator to register an adapter class."""
    def decorator(cls: Type[BaseLLMAdapter]):
        _ADAPTER_REGISTRY[provider_type] = cls
        return cls
    return decorator


def get_adapter_class(provider_type: str) -> Type[BaseLLMAdapter] | None:
    """Get the adapter class for a provider type."""
    return _ADAPTER_REGISTRY.get(provider_type)


def list_adapters() -> list[str]:
    """List all registered adapter types."""
    return list(_ADAPTER_REGISTRY.keys())


# Import adapters to trigger registration
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter

__all__ = [
    "register_adapter",
    "get_adapter_class",
    "list_adapters",
    "OpenAIAdapter",
    "AnthropicAdapter",
]

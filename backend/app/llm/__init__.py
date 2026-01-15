"""
LLM Package - Multi-Model Support Layer

This package provides a unified interface for interacting with various LLM providers,
supporting Native Function Calling across different model APIs.
"""

from .gateway import LLMGateway, get_default_gateway
from .base import BaseLLMAdapter, LLMConfig, LLMResponse, ToolCall, Message

__all__ = [
    "LLMGateway",
    "get_default_gateway",
    "BaseLLMAdapter",
    "LLMConfig",
    "LLMResponse",
    "ToolCall",
    "Message",
]

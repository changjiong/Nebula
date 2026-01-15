"""
LLM Gateway - Unified interface for multi-model support

The gateway manages multiple LLM adapters and routes requests to the appropriate
provider based on configuration or routing strategy.
"""

import uuid
from typing import AsyncIterator

from sqlmodel import Session, select

from app.models import ModelProvider
from .base import (
    BaseLLMAdapter,
    LLMConfig,
    LLMResponse,
    Message,
    StreamChunk,
    ToolDefinition,
)


class LLMGateway:
    """
    Unified gateway for accessing multiple LLM providers.
    
    Features:
    - Dynamic adapter loading based on ModelProvider configuration
    - Provider routing based on model name or explicit selection
    - Fallback handling when primary provider fails
    """
    
    def __init__(self, session: Session | None = None, user_id: uuid.UUID | None = None):
        self.session = session
        self.user_id = user_id
        self._adapters: dict[str, BaseLLMAdapter] = {}
        self._provider_cache: dict[str, ModelProvider] = {}
    
    def get_adapter(self, provider_type: str) -> BaseLLMAdapter | None:
        """Get or create an adapter for the given provider type."""
        if provider_type in self._adapters:
            return self._adapters[provider_type]
        
        # Load provider config from database
        provider = self._get_provider(provider_type)
        if not provider or not provider.api_key:
            return None
        
        # Create adapter
        adapter = self._create_adapter(provider)
        if adapter:
            self._adapters[provider_type] = adapter
        
        return adapter
    
    def _get_provider(self, provider_type: str) -> ModelProvider | None:
        """Get provider configuration from database."""
        if provider_type in self._provider_cache:
            return self._provider_cache[provider_type]
        
        if not self.session:
            return None
        
        query = select(ModelProvider).where(
            ModelProvider.provider_type == provider_type,
            ModelProvider.is_enabled == True,
        )
        if self.user_id:
            query = query.where(ModelProvider.owner_id == self.user_id)
        
        provider = self.session.exec(query).first()
        if provider:
            self._provider_cache[provider_type] = provider
        
        return provider
    
    def _create_adapter(self, provider: ModelProvider) -> BaseLLMAdapter | None:
        """Create an adapter instance based on provider type."""
        from .adapters import get_adapter_class
        
        adapter_class = get_adapter_class(provider.provider_type)
        if not adapter_class:
            return None
        
        return adapter_class(
            api_key=provider.api_key,
            api_url=provider.api_url if provider.api_url else None,
        )
    
    def infer_provider(self, model: str) -> str:
        """Infer provider type from model name."""
        model_lower = model.lower()
        
        # Model name patterns to provider mapping
        patterns = {
            "gpt": "openai",
            "o1": "openai",
            "claude": "anthropic",
            "gemini": "gemini",
            "qwen": "qwen",
            "deepseek": "deepseek",
            "glm": "zhipu",
            "moonshot": "moonshot",
            "ernie": "baidu",
        }
        
        for pattern, provider in patterns.items():
            if pattern in model_lower:
                return provider
        
        # Default to OpenAI-compatible
        return "openai"
    
    async def chat(
        self,
        messages: list[Message],
        config: LLMConfig,
        provider_type: str | None = None,
    ) -> LLMResponse:
        """
        Send a chat request through the gateway.
        
        Args:
            messages: Conversation history
            config: LLM configuration
            provider_type: Explicit provider (inferred from model if not provided)
            
        Returns:
            LLMResponse with content and/or tool calls
        """
        # Determine provider
        provider = provider_type or self.infer_provider(config.model)
        
        # Get adapter
        adapter = self.get_adapter(provider)
        if not adapter:
            raise ValueError(f"No adapter available for provider: {provider}")
        
        # Make request
        return await adapter.chat(messages, config)
    
    async def chat_stream(
        self,
        messages: list[Message],
        config: LLMConfig,
        provider_type: str | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """
        Send a streaming chat request through the gateway.
        """
        provider = provider_type or self.infer_provider(config.model)
        adapter = self.get_adapter(provider)
        
        if not adapter:
            raise ValueError(f"No adapter available for provider: {provider}")
        
        async for chunk in adapter.chat_stream(messages, config):
            yield chunk
    
    async def chat_with_tools(
        self,
        messages: list[Message],
        tools: list[ToolDefinition],
        config: LLMConfig,
        provider_type: str | None = None,
    ) -> LLMResponse:
        """
        Send a chat request with tool definitions (Native Function Calling).
        
        Args:
            messages: Conversation history
            tools: Available tool definitions
            config: LLM configuration (tools will be added from this param)
            provider_type: Explicit provider selection
            
        Returns:
            LLMResponse which may contain tool_calls
        """
        # Add tools to config
        config.tools = tools
        return await self.chat(messages, config, provider_type)
    
    def list_available_providers(self) -> list[str]:
        """List all available (configured and enabled) providers."""
        if not self.session:
            return []
        
        query = select(ModelProvider.provider_type).where(
            ModelProvider.is_enabled == True,
        )
        if self.user_id:
            query = query.where(ModelProvider.owner_id == self.user_id)
        
        return list(self.session.exec(query.distinct()).all())


# Default gateway instance (requires session injection)
_default_gateway: LLMGateway | None = None


def get_default_gateway(session: Session | None = None, user_id: uuid.UUID | None = None) -> LLMGateway:
    """Get or create the default LLM gateway."""
    global _default_gateway
    if _default_gateway is None or session is not None:
        _default_gateway = LLMGateway(session=session, user_id=user_id)
    return _default_gateway

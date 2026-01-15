"""
Base LLM Adapter - Abstract interface for LLM providers

Defines the common interface that all LLM adapters must implement,
supporting Native Function Calling patterns.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator


class MessageRole(str, Enum):
    """Message role types"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """Represents a chat message"""
    role: MessageRole
    content: str | None = None
    tool_calls: list["ToolCall"] | None = None
    tool_call_id: str | None = None  # For tool response messages
    name: str | None = None  # Tool name for tool responses
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to API-friendly dict"""
        result: dict[str, Any] = {"role": self.role.value}
        if self.content is not None:
            result["content"] = self.content
        if self.tool_calls:
            result["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class ToolCall:
    """Represents a tool call from the LLM"""
    id: str
    name: str
    arguments: dict[str, Any]
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to API-friendly dict"""
        import json
        return {
            "id": self.id,
            "type": "function",
            "function": {
                "name": self.name,
                "arguments": json.dumps(self.arguments) if isinstance(self.arguments, dict) else self.arguments,
            }
        }


@dataclass
class ToolDefinition:
    """Tool definition for Native Function Calling"""
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema
    
    def to_openai_format(self) -> dict[str, Any]:
        """Convert to OpenAI function format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }
    
    def to_anthropic_format(self) -> dict[str, Any]:
        """Convert to Anthropic tool format"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }


@dataclass
class LLMConfig:
    """Configuration for LLM calls"""
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    stop: list[str] | None = None
    tools: list[ToolDefinition] | None = None
    tool_choice: str | dict | None = None  # "auto", "none", or specific tool
    stream: bool = False


@dataclass
class LLMResponse:
    """Response from LLM"""
    content: str | None = None
    tool_calls: list[ToolCall] | None = None
    finish_reason: str | None = None
    model: str | None = None
    usage: dict[str, int] | None = None
    
    @property
    def has_tool_calls(self) -> bool:
        """Check if response contains tool calls"""
        return bool(self.tool_calls)
    
    def to_message(self) -> Message:
        """Convert to Message for conversation history"""
        return Message(
            role=MessageRole.ASSISTANT,
            content=self.content,
            tool_calls=self.tool_calls,
        )


@dataclass
class StreamChunk:
    """A chunk from streaming response"""
    content: str | None = None
    tool_call_chunk: dict[str, Any] | None = None
    finish_reason: str | None = None
    is_first: bool = False
    is_last: bool = False


class BaseLLMAdapter(ABC):
    """
    Abstract base class for LLM adapters.
    
    Each adapter implements provider-specific API calls while exposing
    a unified interface for the LLM Gateway.
    """
    
    def __init__(self, api_key: str, api_url: str | None = None):
        self.api_key = api_key
        self.api_url = api_url
    
    @property
    @abstractmethod
    def provider_type(self) -> str:
        """Return the provider type identifier"""
        pass
    
    @property
    @abstractmethod
    def supported_models(self) -> list[str]:
        """Return list of supported model identifiers"""
        pass
    
    @property
    def supports_function_calling(self) -> bool:
        """Whether this provider supports Native Function Calling"""
        return True
    
    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        config: LLMConfig,
    ) -> LLMResponse:
        """
        Send a chat completion request.
        
        Args:
            messages: List of conversation messages
            config: LLM configuration including model, temperature, tools, etc.
            
        Returns:
            LLMResponse with content and/or tool calls
        """
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: list[Message],
        config: LLMConfig,
    ) -> AsyncIterator[StreamChunk]:
        """
        Send a streaming chat completion request.
        
        Args:
            messages: List of conversation messages
            config: LLM configuration
            
        Yields:
            StreamChunk objects with incremental content
        """
        pass
    
    async def test_connection(self) -> tuple[bool, str, list[str]]:
        """
        Test the API connection.
        
        Returns:
            Tuple of (success, message, available_models)
        """
        try:
            # Simple test: send a minimal request
            response = await self.chat(
                messages=[Message(role=MessageRole.USER, content="Hi")],
                config=LLMConfig(model=self.supported_models[0] if self.supported_models else "default", max_tokens=10),
            )
            return True, "Connection successful", self.supported_models
        except Exception as e:
            return False, str(e), []

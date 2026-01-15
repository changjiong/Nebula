"""
Anthropic Claude Adapter

Supports Claude models with Native Function Calling (tool use).
"""

import json
from typing import Any, AsyncIterator

import httpx

from ..base import (
    BaseLLMAdapter,
    LLMConfig,
    LLMResponse,
    Message,
    MessageRole,
    StreamChunk,
    ToolCall,
)
from . import register_adapter


@register_adapter("anthropic")
class AnthropicAdapter(BaseLLMAdapter):
    """
    Adapter for Anthropic Claude API.
    
    Supports tool use (Native Function Calling) with Claude 3+ models.
    """
    
    DEFAULT_URL = "https://api.anthropic.com"
    API_VERSION = "2023-06-01"
    
    SUPPORTED_MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]
    
    def __init__(self, api_key: str, api_url: str | None = None):
        super().__init__(api_key, api_url or self.DEFAULT_URL)
    
    @property
    def provider_type(self) -> str:
        return "anthropic"
    
    @property
    def supported_models(self) -> list[str]:
        return self.SUPPORTED_MODELS
    
    def _build_messages(self, messages: list[Message]) -> tuple[str | None, list[dict[str, Any]]]:
        """
        Convert messages to Anthropic API format.
        
        Returns:
            Tuple of (system_prompt, messages_list)
        """
        system_prompt = None
        result = []
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_prompt = msg.content
                continue
            
            if msg.role == MessageRole.TOOL:
                # Tool result message
                result.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": msg.tool_call_id,
                        "content": msg.content or "",
                    }]
                })
            elif msg.role == MessageRole.ASSISTANT and msg.tool_calls:
                # Assistant message with tool calls
                content = []
                if msg.content:
                    content.append({"type": "text", "text": msg.content})
                for tc in msg.tool_calls:
                    content.append({
                        "type": "tool_use",
                        "id": tc.id,
                        "name": tc.name,
                        "input": tc.arguments,
                    })
                result.append({"role": "assistant", "content": content})
            else:
                # Regular message
                result.append({
                    "role": msg.role.value,
                    "content": msg.content or "",
                })
        
        return system_prompt, result
    
    def _build_tools(self, config: LLMConfig) -> list[dict[str, Any]] | None:
        """Convert tool definitions to Anthropic format."""
        if not config.tools:
            return None
        return [tool.to_anthropic_format() for tool in config.tools]
    
    def _parse_response(self, data: dict) -> LLMResponse:
        """Parse Anthropic API response."""
        content_blocks = data.get("content", [])
        
        text_content = None
        tool_calls = []
        
        for block in content_blocks:
            if block.get("type") == "text":
                text_content = block.get("text", "")
            elif block.get("type") == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.get("id", ""),
                    name=block.get("name", ""),
                    arguments=block.get("input", {}),
                ))
        
        return LLMResponse(
            content=text_content,
            tool_calls=tool_calls if tool_calls else None,
            finish_reason=data.get("stop_reason"),
            model=data.get("model"),
            usage=data.get("usage"),
        )
    
    async def chat(
        self,
        messages: list[Message],
        config: LLMConfig,
    ) -> LLMResponse:
        """Send a chat completion request."""
        url = f"{self.api_url}/v1/messages"
        
        system_prompt, api_messages = self._build_messages(messages)
        
        payload: dict[str, Any] = {
            "model": config.model,
            "messages": api_messages,
            "max_tokens": config.max_tokens,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if config.temperature != 0.7:  # Only include if non-default
            payload["temperature"] = config.temperature
        
        tools = self._build_tools(config)
        if tools:
            payload["tools"] = tools
            if config.tool_choice:
                if config.tool_choice == "auto":
                    payload["tool_choice"] = {"type": "auto"}
                elif config.tool_choice == "none":
                    payload["tool_choice"] = {"type": "none"}
                elif isinstance(config.tool_choice, dict):
                    payload["tool_choice"] = config.tool_choice
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": self.API_VERSION,
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        
        return self._parse_response(data)
    
    async def chat_stream(
        self,
        messages: list[Message],
        config: LLMConfig,
    ) -> AsyncIterator[StreamChunk]:
        """Send a streaming chat completion request."""
        url = f"{self.api_url}/v1/messages"
        
        system_prompt, api_messages = self._build_messages(messages)
        
        payload: dict[str, Any] = {
            "model": config.model,
            "messages": api_messages,
            "max_tokens": config.max_tokens,
            "stream": True,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        tools = self._build_tools(config)
        if tools:
            payload["tools"] = tools
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                url,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": self.API_VERSION,
                    "Content-Type": "application/json",
                },
                json=payload,
            ) as response:
                response.raise_for_status()
                is_first = True
                
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    
                    data_str = line[6:]
                    
                    try:
                        data = json.loads(data_str)
                        event_type = data.get("type")
                        
                        if event_type == "content_block_delta":
                            delta = data.get("delta", {})
                            if delta.get("type") == "text_delta":
                                yield StreamChunk(
                                    content=delta.get("text"),
                                    is_first=is_first,
                                )
                                is_first = False
                            elif delta.get("type") == "input_json_delta":
                                yield StreamChunk(
                                    tool_call_chunk=delta,
                                )
                        
                        elif event_type == "message_stop":
                            yield StreamChunk(is_last=True)
                            break
                        
                    except json.JSONDecodeError:
                        continue

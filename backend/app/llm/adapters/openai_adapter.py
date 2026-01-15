"""
OpenAI-Compatible Adapter

Supports OpenAI API and OpenAI-compatible APIs (DeepSeek, Qwen, Moonshot, etc.)
with Native Function Calling support.
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


@register_adapter("openai")
@register_adapter("deepseek")
@register_adapter("qwen")
@register_adapter("moonshot")
@register_adapter("zhipu")
class OpenAIAdapter(BaseLLMAdapter):
    """
    Adapter for OpenAI and OpenAI-compatible APIs.
    
    Supports:
    - OpenAI (GPT-4, GPT-4o, etc.)
    - DeepSeek (deepseek-chat, deepseek-coder)
    - Qwen (qwen-max, qwen-plus)
    - Moonshot (moonshot-v1-*)
    - Zhipu GLM (glm-4-*)
    """
    
    DEFAULT_URLS = {
        "openai": "https://api.openai.com/v1",
        "deepseek": "https://api.deepseek.com/v1",
        "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "moonshot": "https://api.moonshot.cn/v1",
        "zhipu": "https://open.bigmodel.cn/api/paas/v4",
    }
    
    MODEL_LISTS = {
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "o1-preview", "o1-mini"],
        "deepseek": ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"],
        "qwen": ["qwen-max", "qwen-plus", "qwen-turbo", "qwen-long"],
        "moonshot": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "zhipu": ["glm-4-plus", "glm-4-flash", "glm-4-long"],
    }
    
    def __init__(self, api_key: str, api_url: str | None = None, provider: str = "openai"):
        super().__init__(api_key, api_url)
        self._provider = provider
        if not self.api_url:
            self.api_url = self.DEFAULT_URLS.get(provider, self.DEFAULT_URLS["openai"])
    
    @property
    def provider_type(self) -> str:
        return self._provider
    
    @property
    def supported_models(self) -> list[str]:
        return self.MODEL_LISTS.get(self._provider, self.MODEL_LISTS["openai"])
    
    def _build_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        """Convert messages to OpenAI API format."""
        result = []
        for msg in messages:
            item: dict[str, Any] = {"role": msg.role.value}
            
            if msg.content is not None:
                item["content"] = msg.content
            
            if msg.tool_calls:
                item["tool_calls"] = [tc.to_dict() for tc in msg.tool_calls]
            
            if msg.tool_call_id:
                item["tool_call_id"] = msg.tool_call_id
            
            if msg.name:
                item["name"] = msg.name
            
            result.append(item)
        
        return result
    
    def _build_tools(self, config: LLMConfig) -> list[dict[str, Any]] | None:
        """Convert tool definitions to OpenAI format."""
        if not config.tools:
            return None
        return [tool.to_openai_format() for tool in config.tools]
    
    def _parse_tool_calls(self, tool_calls_data: list[dict]) -> list[ToolCall]:
        """Parse tool calls from API response."""
        result = []
        for tc in tool_calls_data:
            func = tc.get("function", {})
            args_str = func.get("arguments", "{}")
            try:
                args = json.loads(args_str) if isinstance(args_str, str) else args_str
            except json.JSONDecodeError:
                args = {"raw": args_str}
            
            result.append(ToolCall(
                id=tc.get("id", ""),
                name=func.get("name", ""),
                arguments=args,
            ))
        return result
    
    async def chat(
        self,
        messages: list[Message],
        config: LLMConfig,
    ) -> LLMResponse:
        """Send a chat completion request."""
        
        # Experimental: Check for stream context
        from app.llm.stream_context import stream_context_var
        stream_ctx = stream_context_var.get()
        
        if stream_ctx:
            # If context is present, we stream internally and push to queue,
            # then aggregate result to return compatible LLMResponse.
            full_content = ""
            full_reasoning = ""
            tool_calls_dict = {} # accumulate tool calls
            finish_reason = None
            usage = None
            model = config.model
            
            async for chunk in self.chat_stream(messages, config):
                # Push to queue
                await stream_ctx.queue.put(chunk)
                
                # Accumulate for return
                if chunk.content:
                    full_content += chunk.content
                if chunk.reasoning_content:
                    full_reasoning += chunk.reasoning_content
                if chunk.finish_reason:
                    finish_reason = chunk.finish_reason
                if chunk.tool_call_chunk:
                    # Basic accumulation for tool calls (simplified)
                    for tc in chunk.tool_call_chunk:
                        idx = tc.get("index", 0)
                        if idx not in tool_calls_dict:
                            tool_calls_dict[idx] = tc
                        else:
                            # Merge fields
                            existing = tool_calls_dict[idx]
                            if "function" in tc:
                                f = tc["function"]
                                ef = existing.setdefault("function", {})
                                if "name" in f:
                                    ef["name"] = ef.get("name", "") + f["name"]
                                if "arguments" in f:
                                    ef["arguments"] = ef.get("arguments", "") + f["arguments"]
                                    
            # Construct final tool calls
            final_tool_calls = []
            if tool_calls_dict:
                 # Need to implement full parsing logic here or reuse existing method if valid
                 # For now, simplistic reconstruction
                 sorted_tcs = [tool_calls_dict[k] for k in sorted(tool_calls_dict.keys())]
                 final_tool_calls = self._parse_tool_calls(sorted_tcs)

            return LLMResponse(
                content=full_content if full_content else None,
                reasoning_content=full_reasoning if full_reasoning else None,
                tool_calls=final_tool_calls if final_tool_calls else None,
                finish_reason=finish_reason,
                model=model,
                usage=usage
            )

        # Standard non-streaming behavior
        url = f"{self.api_url}/chat/completions"
        
        payload: dict[str, Any] = {
            "model": config.model,
            "messages": self._build_messages(messages),
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
        }
        
        tools = self._build_tools(config)
        if tools:
            payload["tools"] = tools
            if config.tool_choice:
                payload["tool_choice"] = config.tool_choice
        
        if config.stop:
            payload["stop"] = config.stop
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        
        tool_calls = None
        if "tool_calls" in message:
            tool_calls = self._parse_tool_calls(message["tool_calls"])
        
        return LLMResponse(
            content=message.get("content"),
            reasoning_content=message.get("reasoning_content"),
            tool_calls=tool_calls,
            finish_reason=choice.get("finish_reason"),
            model=data.get("model"),
            usage=data.get("usage"),
        )
    
    async def chat_stream(
        self,
        messages: list[Message],
        config: LLMConfig,
    ) -> AsyncIterator[StreamChunk]:
        """Send a streaming chat completion request."""
        url = f"{self.api_url}/chat/completions"
        
        payload: dict[str, Any] = {
            "model": config.model,
            "messages": self._build_messages(messages),
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
            "stream": True,
        }
        
        tools = self._build_tools(config)
        if tools:
            payload["tools"] = tools
            if config.tool_choice:
                payload["tool_choice"] = config.tool_choice
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            ) as response:
                response.raise_for_status()
                is_first = True
                
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    
                    data_str = line[6:]  # Remove "data: " prefix
                    if data_str == "[DONE]":
                        yield StreamChunk(is_last=True)
                        break
                    
                    try:
                        data = json.loads(data_str)
                        choice = data.get("choices", [{}])[0]
                        delta = choice.get("delta", {})
                        
                        chunk = StreamChunk(
                            content=delta.get("content"),
                            reasoning_content=delta.get("reasoning_content"),
                            finish_reason=choice.get("finish_reason"),
                            is_first=is_first,
                        )
                        
                        # Handle tool call chunks
                        if "tool_calls" in delta:
                            chunk.tool_call_chunk = delta["tool_calls"]
                        
                        yield chunk
                        is_first = False
                        
                    except json.JSONDecodeError:
                        continue

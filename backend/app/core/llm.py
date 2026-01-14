"""
Simple LLM client for DeepSeek API.

Provides a straightforward interface to call DeepSeek for chat completions.
"""

import os
from collections.abc import AsyncGenerator

import httpx

from app.core.config import settings


async def stream_chat_completion(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.7,
) -> AsyncGenerator[str, None]:
    """
    Stream chat completion from DeepSeek API.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model name (defaults to settings.LLM_MODEL)
        temperature: Sampling temperature
    
    Yields:
        Token strings as they are generated
    """
    api_key = os.getenv("DEEPSEEK_API_KEY") or settings.DEEPSEEK_API_KEY
    api_base = os.getenv("DEEPSEEK_API_BASE") or settings.DEEPSEEK_API_BASE
    model_name = model or settings.LLM_MODEL

    if api_key == "changethis":
        # Fallback to mock response if API key not configured
        mock_response = ("I am a demo AI assistant. Please configure your "
                        "DEEPSEEK_API_KEY to enable real AI responses.")
        for word in mock_response.split():
            yield word + " "
        return

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            async with client.stream(
                "POST",
                f"{api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model_name,
                    "messages": messages,
                    "stream": True,
                    "temperature": temperature,
                },
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue

                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix

                        if data == "[DONE]":
                            break

                        try:
                            import json
                            chunk = json.loads(data)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")

                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue

        except httpx.HTTPStatusError as e:
            yield f"[Error: API returned {e.response.status_code}] "
        except Exception as e:
            yield f"[Error: {str(e)}] "


async def get_chat_completion(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.7,
) -> str:
    """
    Get complete chat response (non-streaming).
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model name
        temperature: Sampling temperature
    
    Returns:
        Complete response text
    """
    result = ""
    async for token in stream_chat_completion(messages, model, temperature):
        result += token
    return result.strip()

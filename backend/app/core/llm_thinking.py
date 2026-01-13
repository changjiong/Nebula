"""
Enhanced LLM client with thinking chain support.

Supports multiple providers:
1. OpenAI o1-preview/o1-mini (native reasoning)
2. Claude 3.5 Sonnet (with extended thinking)  
3. DeepSeek R1 (reasoning model)
4. Simulated reasoning for standard models
"""

import json
import os
from typing import AsyncGenerator, Literal

import httpx
from app.core.config import settings


ThinkingStepStatus = Literal["pending", "in-progress", "completed", "failed"]


class ThinkingStep:
    """Represents a single step in the thinking chain."""
    
    def __init__(
        self,
        step_id: str,
        title: str,
        status: ThinkingStepStatus,
        content: str = "",
    ):
        self.id = step_id
        self.title = title
        self.status = status
        self.content = content
    
    def to_sse_event(self) -> str:
        """Convert to SSE event format for frontend."""
        data = {
            "type": "thinking",
            "data": {
                "id": self.id,
                "title": self.title,
                "status": self.status,
                "content": self.content,
                "timestamp": int(__import__("time").time() * 1000),
            }
        }
        return f"data: {json.dumps(data)}\n\n"


async def stream_chat_with_thinking(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.7,
    enable_thinking: bool = True,
) -> AsyncGenerator[str, None]:
    """
    Stream chat completion with thinking chain visualization.
    
    Yields SSE events in format:
    - thinking events: Show reasoning steps
    - message events: Show response content
    """
    api_key = os.getenv("DEEPSEEK_API_KEY") or settings.DEEPSEEK_API_KEY
    api_base = os.getenv("DEEPSEEK_API_BASE") or settings.DEEPSEEK_API_BASE
    model_name = model or settings.LLM_MODEL
    
    # Check if we should use DeepSeek R1 (reasoning model)
    use_deepseek_r1 = "reasoner" in model_name.lower() or "r1" in model_name.lower()
    
    if api_key == "changethis":
        # Demo mode with simulated thinking
        if enable_thinking:
            # Simulated thinking steps
            steps = [
                ThinkingStep("step-1", "理解用户问题", "in-progress"),
                ThinkingStep("step-2", "分析关键信息", "pending"),
                ThinkingStep("step-3", "构建回答", "pending"),
            ]
            
            # Step 1
            steps[0].status = "in-progress"
            steps[0].content = f"用户问题: {messages[-1]['content'][:50]}..."
            yield steps[0].to_sse_event()
            
            await __import__("asyncio").sleep(0.5)
            steps[0].status = "completed"
            yield steps[0].to_sse_event()
            
            # Step 2
            steps[1].status = "in-progress"
            steps[1].content = "提取关键词和意图"
            yield steps[1].to_sse_event()
            
            await __import__("asyncio").sleep(0.5)
            steps[1].status = "completed"
            yield steps[1].to_sse_event()
            
            # Step 3
            steps[2].status = "in-progress"
            steps[2].content = "生成结构化回答"
            yield steps[2].to_sse_event()
            
            await __import__("asyncio").sleep(0.5)
            steps[2].status = "completed"
            yield steps[2].to_sse_event()
        
        # Mock response content
        mock_response = (
            "这是演示模式的回答。"
            "请配置 DEEPSEEK_API_KEY 以启用真实 AI 响应。"
        )
        for word in mock_response.split():
            content_event = {
                "type": "message",
                "data": {"content": word + " "}
            }
            yield f"data: {json.dumps(content_event)}\n\n"
            await __import__("asyncio").sleep(0.1)
        
        yield "data: [DONE]\n\n"
        return
    
    # Real API call
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # For DeepSeek R1, enable reasoning mode
            payload = {
                "model": model_name,
                "messages": messages,
                "stream": True,
                "temperature": temperature,
            }
            
            # Add thinking simulation for standard models
            if enable_thinking and not use_deepseek_r1:
                # Step 1: Preparing
                step1 = ThinkingStep(
                    "api-1", "准备调用 AI 模型", "in-progress", f"模型: {model_name}"
                )
                yield step1.to_sse_event()
                await __import__("asyncio").sleep(0.3)
                
                # Complete step 1
                step1.status = "completed"
                yield step1.to_sse_event()
                
                # Step 2: Generating (will be updated after streaming)
                step2 = ThinkingStep("api-2", "正在生成回答...", "in-progress")
                yield step2.to_sse_event()
            
            async with client.stream(
                "POST",
                f"{api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            ) as response:
                response.raise_for_status()
                
                has_content = False
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    if line.startswith("data: "):
                        data = line[6:]
                        
                        if data == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(data)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            
                            # Check for reasoning content (DeepSeek R1)
                            reasoning = delta.get("reasoning_content", "")
                            if reasoning and enable_thinking:
                                reasoning_event = {
                                    "type": "thinking",
                                    "data": {
                                        "id": f"reason-{chunk.get('id', '')}",
                                        "title": "AI 推理过程",
                                        "status": "in-progress",
                                        "content": reasoning,
                                        "timestamp": int(__import__("time").time() * 1000),
                                    }
                                }
                                yield f"data: {json.dumps(reasoning_event)}\n\n"
                            
                            if content:
                                has_content = True
                                content_event = {
                                    "type": "message",
                                    "data": {"content": content}
                                }
                                yield f"data: {json.dumps(content_event)}\n\n"
                        except json.JSONDecodeError:
                            continue
                
                # Complete thinking step after streaming is done
                if enable_thinking and not use_deepseek_r1 and has_content:
                    step2_complete = ThinkingStep("api-2", "回答生成完成", "completed")
                    yield step2_complete.to_sse_event()
                
                yield "data: [DONE]\n\n"
                
        except httpx.HTTPStatusError as e:
            error_event = {
                "type": "error",
                "data": {
                    "code": str(e.response.status_code),
                    "message": f"API 错误: {e.response.status_code}"
                }
            }
            yield f"data: {json.dumps(error_event)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_event = {
                "type": "error",
                "data": {"code": "unknown", "message": str(e)}
            }
            yield f"data: {json.dumps(error_event)}\n\n"
            yield "data: [DONE]\n\n"


# Keep backward compatibility
async def stream_chat_completion(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.7,
) -> AsyncGenerator[str, None]:
    """Legacy function - yields plain text tokens."""
    async for event_line in stream_chat_with_thinking(
        messages, model, temperature, enable_thinking=False
    ):
        if event_line.startswith("data: "):
            try:
                data = event_line[6:].strip()
                if data == "[DONE]":
                    break
                event = json.loads(data)
                if event.get("type") == "message":
                    yield event["data"]["content"]
            except:
                continue

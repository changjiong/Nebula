"""
Planner Layer - Intent Understanding and Agent Routing

Provides intent classification, agent routing, and parameter extraction
for the LangGraph agent orchestration engine.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from langchain_core.messages import BaseMessage

from app.llm import LLMGateway
from app.llm.base import LLMConfig, Message, MessageRole
import json


class IntentType(str, Enum):
    """Supported intent types for agent routing."""

    QUERY = "query"  # Data query/retrieval
    ANALYSIS = "analysis"  # Data analysis/insights
    PREDICTION = "prediction"  # ML model predictions
    WORKFLOW = "workflow"  # Multi-step workflows
    CONVERSATION = "conversation"  # General chat
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Represents a classified user intent."""

    type: IntentType
    confidence: float
    sub_type: str | None = None
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedParams:
    """Container for parameters extracted from user input."""

    entities: dict[str, Any] = field(default_factory=dict)
    filters: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""

    def get(self, key: str, default: Any = None) -> Any:
        """Get a parameter value from any category."""
        if key in self.entities:
            return self.entities[key]
        if key in self.filters:
            return self.filters[key]
        if key in self.options:
            return self.options[key]
        return default

    def to_dict(self) -> dict[str, Any]:
        """Convert to flat dictionary."""
        return {
            **self.entities,
            **self.filters,
            **self.options,
            "_raw_text": self.raw_text,
        }


@dataclass
class RoutingDecision:
    """Result of agent routing decision."""

    target_agent: str
    intent: Intent
    params: ExtractedParams
    priority: int = 0
    fallback_agents: list[str] = field(default_factory=list)


class IntentClassifier(ABC):
    """
    Abstract base class for intent classification.

    Implementations can use rule-based, ML, or LLM-based approaches.
    """

    @abstractmethod
    async def classify(
        self, message: str, context: list[BaseMessage] | None = None
    ) -> Intent:
        """Classify user intent from message and optional context."""
        ...


class RuleBasedClassifier(IntentClassifier):
    """
    Rule-based intent classifier using keyword matching.

    Suitable for well-defined, predictable intents.
    """

    def __init__(self) -> None:
        self._rules: dict[IntentType, list[str]] = {
            IntentType.QUERY: [
                "查询",
                "查找",
                "获取",
                "显示",
                "列出",
                "search",
                "find",
                "get",
                "show",
                "list",
            ],
            IntentType.ANALYSIS: [
                "分析",
                "统计",
                "汇总",
                "趋势",
                "对比",
                "analyze",
                "statistics",
                "trend",
                "compare",
            ],
            IntentType.PREDICTION: [
                "预测",
                "预估",
                "评估",
                "风险",
                "评分",
                "predict",
                "forecast",
                "estimate",
                "risk",
                "score",
            ],
            IntentType.WORKFLOW: [
                "流程",
                "审批",
                "提交",
                "创建",
                "执行",
                "workflow",
                "approve",
                "submit",
                "create",
                "execute",
            ],
        }

    async def classify(
        self, message: str, context: list[BaseMessage] | None = None
    ) -> Intent:
        """Classify intent using keyword matching."""
        message_lower = message.lower()

        for intent_type, keywords in self._rules.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return Intent(
                        type=intent_type,
                        confidence=0.8,
                        description=f"Matched keyword: {keyword}",
                    )

        # Default to conversation if no match
        return Intent(
            type=IntentType.CONVERSATION,
            confidence=0.5,
            description="No specific intent matched",
        )


class ParameterExtractor(ABC):
    """
    Abstract base class for parameter extraction.

    Extracts structured parameters from natural language input.
    """

    @abstractmethod
    async def extract(
        self,
        message: str,
        intent: Intent,
        context: list[BaseMessage] | None = None,
    ) -> ExtractedParams:
        """Extract parameters based on message and classified intent."""
        ...


class BasicParameterExtractor(ParameterExtractor):
    """
    Basic parameter extractor using pattern matching.

    Extracts common patterns like dates, numbers, and known entities.
    """

    def __init__(self) -> None:
        self._entity_patterns: dict[str, list[str]] = {
            "time_range": ["今天", "昨天", "本周", "本月", "今年", "today", "yesterday"],
            "limit": ["前", "个", "条", "top"],
        }

    async def extract(
        self,
        message: str,
        intent: Intent,
        context: list[BaseMessage] | None = None,
    ) -> ExtractedParams:
        """Extract basic parameters using pattern matching."""
        params = ExtractedParams(raw_text=message)

        # Extract time-related entities
        for time_word in self._entity_patterns["time_range"]:
            if time_word in message:
                params.filters["time_range"] = time_word
                break

        # Extract numeric limits
        import re

        limit_match = re.search(r"前\s*(\d+)\s*[个条]|top\s*(\d+)", message.lower())
        if limit_match:
            limit = limit_match.group(1) or limit_match.group(2)
            params.options["limit"] = int(limit)

        return params


class AgentRouter:
    """
    Routes requests to appropriate agents based on intent.

    Maps intents to agent handlers and manages fallback logic.
    """

    def __init__(self) -> None:
        self._agent_registry: dict[IntentType, str] = {
            IntentType.QUERY: "data_query_agent",
            IntentType.ANALYSIS: "analytics_agent",
            IntentType.PREDICTION: "prediction_agent",
            IntentType.WORKFLOW: "workflow_agent",
            IntentType.CONVERSATION: "chat_agent",
            IntentType.UNKNOWN: "chat_agent",
        }
        self._fallback_map: dict[str, list[str]] = {
            "data_query_agent": ["analytics_agent", "chat_agent"],
            "analytics_agent": ["data_query_agent", "chat_agent"],
            "prediction_agent": ["analytics_agent", "chat_agent"],
            "workflow_agent": ["chat_agent"],
        }

    def register_agent(
        self,
        intent_type: IntentType,
        agent_name: str,
        fallbacks: list[str] | None = None,
    ) -> None:
        """Register an agent for a specific intent type."""
        self._agent_registry[intent_type] = agent_name
        if fallbacks:
            self._fallback_map[agent_name] = fallbacks

    def route(self, intent: Intent, params: ExtractedParams) -> RoutingDecision:
        """Determine target agent based on intent."""
        agent = self._agent_registry.get(intent.type, "chat_agent")
        fallbacks = self._fallback_map.get(agent, ["chat_agent"])

        return RoutingDecision(
            target_agent=agent,
            intent=intent,
            params=params,
            priority=self._calculate_priority(intent),
            fallback_agents=fallbacks,
        )

    def _calculate_priority(self, intent: Intent) -> int:
        """Calculate execution priority based on intent type."""
        priority_map = {
            IntentType.WORKFLOW: 10,
            IntentType.PREDICTION: 8,
            IntentType.ANALYSIS: 6,
            IntentType.QUERY: 4,
            IntentType.CONVERSATION: 2,
            IntentType.UNKNOWN: 0,
        }
        return priority_map.get(intent.type, 0)


class Planner:
    """
    Main planner component that orchestrates intent classification,
    parameter extraction, and agent routing.

    Acts as a LangGraph node for the planning phase.
    """

    def __init__(
        self,
        classifier: IntentClassifier | None = None,
        extractor: ParameterExtractor | None = None,
        router: AgentRouter | None = None,
    ) -> None:
        self.classifier = classifier or RuleBasedClassifier()
        self.extractor = extractor or BasicParameterExtractor()
        self.router = router or AgentRouter()

    async def plan(
        self,
        message: str,
        context: list[BaseMessage] | None = None,
    ) -> RoutingDecision:
        """
        Execute full planning pipeline:
        1. Classify intent
        2. Extract parameters
        3. Route to appropriate agent
        """
        # Classify intent
        intent = await self.classifier.classify(message, context)

        # Extract parameters
        params = await self.extractor.extract(message, intent, context)

        # Route to agent
        decision = self.router.route(intent, params)

        return decision

    async def __call__(
        self, state: dict[str, Any]
    ) -> dict[str, Any]:
        """LangGraph node interface for planning."""
        message = state.get("input", "")
        context = state.get("messages", [])

        decision = await self.plan(message, context)

        return {
            **state,
            "intent": decision.intent.type.value,
            "intent_confidence": decision.intent.confidence,
            "target_agent": decision.target_agent,
            "extracted_params": decision.params.to_dict(),
            "fallback_agents": decision.fallback_agents,
        }


class LLMPlanner(Planner):
    """
    LLM-based planner that uses an LLM to perceive intent and plan steps.
    """

    def __init__(self, gateway: LLMGateway) -> None:
        self.gateway = gateway
        # Initialize default components as fallback
        super().__init__()

    async def plan(
        self,
        message: str,
        context: list[BaseMessage] | list[dict] | None = None,
        model: str = "deepseek-chat",
    ) -> RoutingDecision:
        """
        Execute planning using LLM.
        """
        # Include prior conversation context (if any) to reduce ambiguity on follow-ups.
        context_text = ""
        if context:
            try:
                # state["messages"] in this project is often a list[dict]
                if isinstance(context[0], dict):  # type: ignore[index]
                    items = []
                    for msg in context[-12:]:  # keep context small
                        role = str(msg.get("role", "user"))
                        content = str(msg.get("content", "")).strip()
                        if not content:
                            continue
                        items.append(f"{role}: {content}")
                    if items:
                        context_text = "\n\nConversation Context:\n" + "\n".join(items)
                else:
                    # Fallback: BaseMessage-like objects (LangChain)
                    items = []
                    for msg in context[-12:]:  # type: ignore[index]
                        role = getattr(msg, "type", None) or getattr(msg, "role", "user")
                        content = getattr(msg, "content", "")
                        if isinstance(content, str) and content.strip():
                            items.append(f"{role}: {content.strip()}")
                    if items:
                        context_text = "\n\nConversation Context:\n" + "\n".join(items)
            except Exception:
                # If context formatting fails, silently ignore (planning can proceed without it).
                context_text = ""

        # specialized prompt for planning
        prompt = f"""You are an advanced AI agent planner.
Your goal is to Perceive the user's request, Understand their intent, and Plan the steps to fulfill it.

User Request: {message}{context_text}

Analyze the request and output a VALID JSON object with the following structure:
{{
  "intent": "query" | "analysis" | "prediction" | "workflow" | "conversation" | "unknown",
  "confidence": 0.0-1.0,
  "reasoning": "Explain your perception of the user's need. Why this intent? What is the user trying to achieve? What is the context?",
  "plan_steps": [
    "Step 1: ...",
    "Step 2: ..."
  ],
  "entities": {{
    "key": "value"
  }}
}}

Be explicit in your reasoning.
- For simple greetings (e.g., "Hello"), the plan should be to respond politely.
- For complex requests, break them down into logical steps that might involve tool calls.
- "reasoning" is your PERCEPTION phase.
- "plan_steps" is your PLANNING phase.
"""
        
        try:
             # Check for active stream context
             from app.llm.stream_context import stream_context_var
             ctx = stream_context_var.get()
             
             content = ""
             
             if ctx:
                 # Stream mode: Forward reasoning, accumulate content
                 async for chunk in self.gateway.chat_stream(
                    messages=[Message(role=MessageRole.USER, content=prompt)],
                    config=LLMConfig(
                        model=model, # Use dynamic model
                        temperature=0.0,
                    )
                 ):
                     # Forward reasoning chunks to the global stream queue
                     # This makes the "Thinking Process" visible to the user immediately
                     if chunk.reasoning_content:
                         await ctx.queue.put(chunk)
                     
                     # Accumulate content (JSON) but DO NOT forward it
                     # We want to hide the raw JSON plan from the user
                     if chunk.content:
                         content += chunk.content
             else:
                 # Sync mode (fallback or no stream)
                 response = await self.gateway.chat(
                    messages=[Message(role=MessageRole.USER, content=prompt)],
                    config=LLMConfig(
                        model=model, # Use dynamic model
                        temperature=0.0,
                        # response_format={"type": "json_object"} # Not supported by base config yet
                    )
                )
                 content = response.content
             
             # clean markdown codes if any
             content = content.replace("```json", "").replace("```", "").strip()
             
             data = json.loads(content)
             
             intent_str = data.get("intent", "conversation").upper()
             try:
                 intent_type = IntentType(intent_str.lower())
             except ValueError:
                 intent_type = IntentType.CONVERSATION
                 
             intent = Intent(
                 type=intent_type,
                 confidence=data.get("confidence", 0.5),
                 description=data.get("reasoning", ""),
                 metadata={
                     "plan_steps": data.get("plan_steps", []),
                     "reasoning": data.get("reasoning", "")
                 }
             )
             
             params = ExtractedParams(
                 entities=data.get("entities", {}),
                 raw_text=message
             )
             
             # Use router logic to pick agent based on intent
             decision = self.router.route(intent, params)
             return decision
             
        except Exception as e:
            print(f"LLM Planning failed: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to rule-based
            return await super().plan(message, context)


# Default planner instance
default_planner = Planner()

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


# Default planner instance
default_planner = Planner()

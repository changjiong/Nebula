"""
Agent Module

Agent definition framework with:
- BaseAgent: Abstract base class for all agents
- AgentRegistry: Dynamic agent registration and discovery
- @register_agent: Decorator for auto-registration
"""

from app.agent.base import (
    AgentConfig,
    AgentInput,
    AgentOutput,
    AgentServiceConfig,
    BaseAgent,
)
from app.agent.registry import (
    AgentRegistry,
    ToolRegistry,
    discover_agents,
    register_agent,
    register_tool,
)

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentInput",
    "AgentOutput",
    "AgentConfig",
    "AgentServiceConfig",
    # Registry
    "AgentRegistry",
    "ToolRegistry",
    "register_agent",
    "register_tool",
    "discover_agents",
]

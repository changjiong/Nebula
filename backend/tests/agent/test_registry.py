"""
Tests for Agent Registry
"""

import pytest

from app.agent.base import AgentOutput, BaseAgent
from app.agent.registry import (
    AgentRegistry,
    ToolRegistry,
    register_agent,
    register_tool,
)


class TestAgentRegistry:
    @pytest.fixture(autouse=True)
    def clean_registry(self):
        """Clean registry before and after tests."""
        AgentRegistry.clear()
        yield
        AgentRegistry.clear()

    @pytest.mark.anyio
    async def test_register_decorator(self):
        """Test @register_agent decorator."""

        @register_agent
        class MyAgent(BaseAgent):
            name = "my_agent"

            async def execute(self, input_data):
                return AgentOutput()

        # Check registration
        assert AgentRegistry.get("my_agent") == MyAgent
        agents = AgentRegistry.list_agents()
        assert ("my_agent", MyAgent) in agents

    @pytest.mark.anyio
    async def test_register_decorator_with_name(self):
        """Test @register_agent(name="...")."""

        @register_agent(name="custom_name")
        class MyAgent(BaseAgent):
            name = "original_name"

            async def execute(self, input_data):
                return AgentOutput()

        # Check registration with custom name
        assert AgentRegistry.get("custom_name") == MyAgent
        assert AgentRegistry.get("original_name") is None

    @pytest.mark.anyio
    async def test_get_instance(self):
        """Test getting singleton instance."""

        @register_agent
        class MyAgent(BaseAgent):
            name = "my_agent"

            async def execute(self, input_data):
                return AgentOutput()

        # First retrieval
        instance1 = AgentRegistry.get_instance("my_agent")
        assert instance1 is not None
        assert isinstance(instance1, MyAgent)

        # Second retrieval (should be same instance)
        instance2 = AgentRegistry.get_instance("my_agent")
        assert instance1 is instance2

    @pytest.mark.anyio
    async def test_unregister(self):
        """Test unregistering agents."""

        @register_agent
        class MyAgent(BaseAgent):
            name = "my_agent"

            async def execute(self, input_data):
                return AgentOutput()

        assert AgentRegistry.get("my_agent") is not None
        assert AgentRegistry.unregister("my_agent") is True
        assert AgentRegistry.get("my_agent") is None
        assert AgentRegistry.unregister("my_agent") is False


class TestToolRegistry:
    @pytest.fixture(autouse=True)
    def clean_registry(self):
        """Clean registry before and after tests."""
        ToolRegistry.clear()
        yield
        ToolRegistry.clear()

    def test_register_tool_decorator(self):
        """Test @register_tool decorator."""

        @register_tool
        def my_tool(x):
            return x

        assert ToolRegistry.get("my_tool") == my_tool
        tools = ToolRegistry.list_tools()
        assert ("my_tool", my_tool) in tools

    def test_register_tool_with_name(self):
        """Test @register_tool(name="...")."""

        @register_tool(name="custom_tool")
        def my_tool(x):
            return x

        assert ToolRegistry.get("custom_tool") == my_tool
        assert ToolRegistry.get("my_tool") is None

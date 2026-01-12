"""
Tests for Agent Base Classes
"""

import pytest
from pydantic import ValidationError

from app.agent.base import AgentConfig, AgentFieldConfig, AgentInput, BaseAgent


class TestConfig:
    def test_field_config_validation(self):
        """Test AgentFieldConfig validation."""
        # Valid config
        field = AgentFieldConfig(name="test_field", type="string")
        assert field.name == "test_field"
        assert field.type == "string"
        assert field.required is True  # default
        assert field.default is None

        # Invalid config (missing name)
        with pytest.raises(ValidationError):
            AgentFieldConfig(type="string")  # type: ignore

    def test_agent_config_validation(self):
        """Test AgentConfig validation."""
        # Valid config
        config = AgentConfig(
            name="test_agent",
            version="1.0.0",
            description="Test agent",
            input=[AgentFieldConfig(name="q", type="string")],
            output=[AgentFieldConfig(name="r", type="object")],
        )
        assert config.name == "test_agent"
        assert len(config.input) == 1
        assert len(config.output) == 1

        # Invalid config (missing name)
        with pytest.raises(ValidationError):
            AgentConfig(version="1.0.0")  # type: ignore


class TestBaseAgent:
    def test_abstract_class(self):
        """Test that BaseAgent cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseAgent()  # type: ignore

    @pytest.mark.anyio
    async def test_subclass_implementation(self):
        """Test proper subclassing of BaseAgent."""

        class MyAgent(BaseAgent):
            name = "my_agent"

            async def execute(self, input_data):
                return {"result": "ok"}

        agent = MyAgent()
        assert agent.name == "my_agent"
        assert agent.version == "1.0.0"

        result = await agent.execute(None)
        assert result == {"result": "ok"}

    def test_input_validation(self):
        """Test input validation logic."""

        class ValidatingAgent(BaseAgent):
            name = "validating_agent"

            # Manually set config for testing
            _config = AgentConfig(
                name="validating_agent",
                input=[
                    AgentFieldConfig(name="req_str", type="string", required=True),
                    AgentFieldConfig(name="opt_int", type="int", required=False),
                ],
            )

            async def execute(self, input_data):
                pass

        agent = ValidatingAgent()

        # Valid input
        valid_input = {"req_str": "hello", "opt_int": 123}
        errors = agent.validate_input(valid_input)
        assert len(errors) == 0

        # Invalid input (missing required)
        invalid_input_1 = {"opt_int": 123}
        errors_1 = agent.validate_input(invalid_input_1)
        assert len(errors_1) == 1
        assert "Missing required field" in errors_1[0]

        # Invalid input (wrong type)
        invalid_input_2 = {"req_str": 123}
        errors_2 = agent.validate_input(invalid_input_2)
        assert len(errors_2) == 1
        assert "must be a string" in errors_2[0]


class TestAgentInput:
    def test_input_schema(self):
        """Test AgentInput schema behavior."""

        class MyInput(AgentInput):
            query: str

        # Valid input
        input_data = MyInput(query="test")
        assert input_data.query == "test"

        # Extra fields allowed
        input_data = MyInput(query="test", extra_field=123)
        assert input_data.extra_field == 123

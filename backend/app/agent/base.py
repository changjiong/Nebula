"""
Agent Base Classes

Defines the core abstractions for Agent definitions:
- AgentInput: Input schema for agents
- AgentOutput: Output schema for agents
- AgentConfig: Configuration loaded from YAML
- BaseAgent: Abstract base class with execution interface
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class AgentFieldConfig(BaseModel):
    """Configuration for a single input/output field."""

    name: str = Field(..., description="Field name")
    type: str = Field(..., description="Field type (string, int, float, array, object)")
    required: bool = Field(default=True, description="Whether field is required")
    description: str = Field(default="", description="Field description")
    default: Any = Field(default=None, description="Default value")


class AgentServiceConfig(BaseModel):
    """Configuration for an external service call."""

    name: str = Field(..., description="Service adapter name")
    endpoint: str = Field(default="", description="API endpoint")
    method: str = Field(default="POST", description="HTTP method")
    model: str = Field(default="", description="Model name for model factory")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retries on failure")


class AgentConfig(BaseModel):
    """Agent configuration loaded from YAML."""

    name: str = Field(..., description="Agent unique identifier")
    version: str = Field(default="1.0.0", description="Agent version")
    description: str = Field(default="", description="Agent description")
    input: list[AgentFieldConfig] = Field(
        default_factory=list, description="Input field definitions"
    )
    output: list[AgentFieldConfig] = Field(
        default_factory=list, description="Output field definitions"
    )
    services: list[AgentServiceConfig] = Field(
        default_factory=list, description="External service configurations"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @classmethod
    def from_yaml(cls, yaml_path: Path | str) -> "AgentConfig":
        """Load configuration from a YAML file.

        Args:
            yaml_path: Path to the config.yaml file

        Returns:
            AgentConfig instance

        Raises:
            FileNotFoundError: If yaml_path doesn't exist
            ValueError: If YAML is invalid
        """
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid YAML config: expected dict, got {type(data)}")

        return cls(**data)


class AgentInput(BaseModel):
    """Base class for agent input.

    Agents should subclass this to define their specific input schema.
    """

    model_config = {"extra": "allow"}


class AgentOutput(BaseModel):
    """Base class for agent output.

    Agents should subclass this to define their specific output schema.
    """

    success: bool = Field(default=True, description="Whether execution succeeded")
    error: str | None = Field(default=None, description="Error message if failed")
    data: dict[str, Any] = Field(
        default_factory=dict, description="Output data"
    )

    model_config = {"extra": "allow"}


class BaseAgent(ABC):
    """Abstract base class for all agents.

    Agents define:
    - Input/output schemas
    - Configuration from YAML
    - Execution logic

    Example:
        ```python
        from app.agent import BaseAgent, register_agent

        @register_agent
        class MyAgent(BaseAgent):
            name = "my_agent"

            async def execute(self, input: AgentInput) -> AgentOutput:
                # Agent logic here
                return AgentOutput(data={"result": "success"})
        ```
    """

    # Class attributes - should be overridden by subclasses
    name: str = ""
    description: str = ""
    version: str = "1.0.0"

    # Configuration loaded from config.yaml
    _config: AgentConfig | None = None

    def __init__(self) -> None:
        """Initialize the agent and load configuration."""
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from config.yaml in the agent's directory."""
        # Get the directory containing the agent module
        agent_module = self.__class__.__module__
        if agent_module and "." in agent_module:
            # e.g., "app.agent.enterprise_resolver.handler" -> find config.yaml
            import importlib

            module = importlib.import_module(agent_module)
            if hasattr(module, "__file__") and module.__file__:
                config_path = Path(module.__file__).parent / "config.yaml"
                if config_path.exists():
                    self._config = AgentConfig.from_yaml(config_path)
                    # Update class attributes from config if not set
                    if not self.name and self._config.name:
                        self.name = self._config.name
                    if not self.description and self._config.description:
                        self.description = self._config.description
                    if self._config.version:
                        self.version = self._config.version

    @property
    def config(self) -> AgentConfig | None:
        """Get the agent configuration."""
        return self._config

    def get_service_config(self, service_name: str) -> AgentServiceConfig | None:
        """Get configuration for a specific service.

        Args:
            service_name: Name of the service

        Returns:
            Service configuration or None if not found
        """
        if not self._config:
            return None
        for svc in self._config.services:
            if svc.name == service_name:
                return svc
        return None

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate input against the configured schema.

        Args:
            input_data: Input data to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors: list[str] = []
        if not self._config:
            return errors

        for field in self._config.input:
            if field.required and field.name not in input_data:
                errors.append(f"Missing required field: {field.name}")
            elif field.name in input_data:
                value = input_data[field.name]
                # Basic type validation
                if field.type == "string" and not isinstance(value, str):
                    errors.append(f"Field {field.name} must be a string")
                elif field.type == "int" and not isinstance(value, int):
                    errors.append(f"Field {field.name} must be an integer")
                elif field.type == "float" and not isinstance(value, int | float):
                    errors.append(f"Field {field.name} must be a number")
                elif field.type == "array" and not isinstance(value, list):
                    errors.append(f"Field {field.name} must be an array")
                elif field.type == "object" and not isinstance(value, dict):
                    errors.append(f"Field {field.name} must be an object")

        return errors

    @abstractmethod
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Execute the agent logic.

        Args:
            input_data: Input data for the agent

        Returns:
            Agent execution output

        This method must be implemented by subclasses.
        """
        ...

    async def __call__(self, input_data: AgentInput) -> AgentOutput:
        """Make the agent callable.

        Args:
            input_data: Input data for the agent

        Returns:
            Agent execution output
        """
        return await self.execute(input_data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, version={self.version})>"

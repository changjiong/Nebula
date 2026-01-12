"""
Agent and Tool Registry

Provides dynamic registration and discovery of agents and tools:
- AgentRegistry: Singleton for agent registration
- ToolRegistry: Singleton for tool registration
- @register_agent: Decorator for auto-registration
- @register_tool: Decorator for tool registration
- discover_agents(): Auto-discover agents from filesystem
"""

import importlib
import logging
from pathlib import Path
from typing import Any, TypeVar

from app.agent.base import BaseAgent

logger = logging.getLogger(__name__)

# Type variable for agent classes
T = TypeVar("T", bound=BaseAgent)


class AgentRegistry:
    """Singleton registry for agents.

    Agents are registered by name and can be retrieved or listed.

    Example:
        ```python
        # Register an agent
        AgentRegistry.register(MyAgent)

        # Get an agent by name
        agent_cls = AgentRegistry.get("my_agent")
        agent = agent_cls()
        result = await agent.execute(input_data)

        # List all agents
        for name, cls in AgentRegistry.list_agents():
            print(f"{name}: {cls}")
        ```
    """

    _agents: dict[str, type[BaseAgent]] = {}
    _instances: dict[str, BaseAgent] = {}

    @classmethod
    def register(cls, agent_cls: type[BaseAgent], name: str | None = None) -> None:
        """Register an agent class.

        Args:
            agent_cls: The agent class to register
            name: Optional name override (defaults to agent_cls.name)
        """
        agent_name = name or getattr(agent_cls, "name", "") or agent_cls.__name__
        if not agent_name:
            raise ValueError(f"Agent class {agent_cls} must have a 'name' attribute")

        if agent_name in cls._agents:
            logger.warning(f"Agent '{agent_name}' is already registered, overwriting")

        cls._agents[agent_name] = agent_cls
        logger.info(f"Registered agent: {agent_name}")

    @classmethod
    def unregister(cls, name: str) -> bool:
        """Unregister an agent by name.

        Args:
            name: Agent name to unregister

        Returns:
            True if agent was unregistered, False if not found
        """
        if name in cls._agents:
            del cls._agents[name]
            if name in cls._instances:
                del cls._instances[name]
            return True
        return False

    @classmethod
    def get(cls, name: str) -> type[BaseAgent] | None:
        """Get an agent class by name.

        Args:
            name: Agent name

        Returns:
            Agent class or None if not found
        """
        return cls._agents.get(name)

    @classmethod
    def get_instance(cls, name: str) -> BaseAgent | None:
        """Get or create a singleton instance of an agent.

        Args:
            name: Agent name

        Returns:
            Agent instance or None if not found
        """
        if name not in cls._instances:
            agent_cls = cls.get(name)
            if agent_cls:
                cls._instances[name] = agent_cls()
        return cls._instances.get(name)

    @classmethod
    def list_agents(cls) -> list[tuple[str, type[BaseAgent]]]:
        """List all registered agents.

        Returns:
            List of (name, class) tuples
        """
        return list(cls._agents.items())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered agents (useful for testing)."""
        cls._agents.clear()
        cls._instances.clear()


class ToolRegistry:
    """Singleton registry for tools.

    Tools are helper functions that can be used by agents.
    """

    _tools: dict[str, Any] = {}

    @classmethod
    def register(cls, tool_func: Any, name: str | None = None) -> None:
        """Register a tool function.

        Args:
            tool_func: The tool function to register
            name: Optional name override (defaults to function name)
        """
        tool_name = name or getattr(tool_func, "__name__", str(tool_func))
        if tool_name in cls._tools:
            logger.warning(f"Tool '{tool_name}' is already registered, overwriting")

        cls._tools[tool_name] = tool_func
        logger.info(f"Registered tool: {tool_name}")

    @classmethod
    def unregister(cls, name: str) -> bool:
        """Unregister a tool by name.

        Args:
            name: Tool name to unregister

        Returns:
            True if tool was unregistered, False if not found
        """
        if name in cls._tools:
            del cls._tools[name]
            return True
        return False

    @classmethod
    def get(cls, name: str) -> Any | None:
        """Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool function or None if not found
        """
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> list[tuple[str, Any]]:
        """List all registered tools.

        Returns:
            List of (name, function) tuples
        """
        return list(cls._tools.items())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered tools (useful for testing)."""
        cls._tools.clear()


def register_agent(
    cls: type[T] | None = None, *, name: str | None = None
) -> type[T] | Any:
    """Decorator to register an agent class.

    Can be used with or without arguments:

    ```python
    @register_agent
    class MyAgent(BaseAgent):
        name = "my_agent"
        ...

    @register_agent(name="custom_name")
    class AnotherAgent(BaseAgent):
        ...
    ```

    Args:
        cls: The agent class (when used without arguments)
        name: Optional custom name for registration

    Returns:
        The decorated class (unchanged)
    """

    def decorator(agent_cls: type[T]) -> type[T]:
        AgentRegistry.register(agent_cls, name=name)
        return agent_cls

    if cls is not None:
        # Decorator used without arguments: @register_agent
        return decorator(cls)
    else:
        # Decorator used with arguments: @register_agent(name="...")
        return decorator


def register_tool(
    func: Any | None = None, *, name: str | None = None
) -> Any:
    """Decorator to register a tool function.

    Can be used with or without arguments:

    ```python
    @register_tool
    def my_tool(x: int) -> str:
        ...

    @register_tool(name="custom_name")
    def another_tool(x: int) -> str:
        ...
    ```

    Args:
        func: The tool function (when used without arguments)
        name: Optional custom name for registration

    Returns:
        The decorated function (unchanged)
    """

    def decorator(tool_func: Any) -> Any:
        ToolRegistry.register(tool_func, name=name)
        return tool_func

    if func is not None:
        # Decorator used without arguments: @register_tool
        return decorator(func)
    else:
        # Decorator used with arguments: @register_tool(name="...")
        return decorator


def discover_agents(base_path: Path | str | None = None) -> list[str]:
    """Auto-discover and register agents from the filesystem.

    Looks for agent directories under base_path that contain:
    - __init__.py
    - config.yaml
    - handler.py (with an agent class)

    Args:
        base_path: Base path to search (defaults to app/agent directory)

    Returns:
        List of discovered agent names
    """
    if base_path is None:
        base_path = Path(__file__).parent
    else:
        base_path = Path(base_path)

    discovered: list[str] = []

    # Skip special directories
    skip_dirs = {"__pycache__", "_template"}

    for item in base_path.iterdir():
        if not item.is_dir():
            continue
        if item.name.startswith("_") or item.name in skip_dirs:
            continue

        # Check for required files
        init_file = item / "__init__.py"
        config_file = item / "config.yaml"
        handler_file = item / "handler.py"

        if not (init_file.exists() and config_file.exists() and handler_file.exists()):
            continue

        try:
            # Import the handler module to trigger registration
            module_name = f"app.agent.{item.name}.handler"
            importlib.import_module(module_name)
            discovered.append(item.name)
            logger.info(f"Discovered agent: {item.name}")
        except Exception as e:
            logger.error(f"Failed to load agent {item.name}: {e}")

    return discovered

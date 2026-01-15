"""
Tool Executor - Unified tool execution layer

This module provides a unified interface for executing tools registered
in the knowledge engineering system, supporting both DB-defined tools
and built-in tools.
"""

import json
import time
from typing import Any
from datetime import datetime

from sqlmodel import Session, select

from app.models import Tool


class ToolExecutionError(Exception):
    """Exception raised when tool execution fails."""

    def __init__(self, tool_name: str, message: str):
        self.tool_name = tool_name
        self.message = message
        super().__init__(f"Tool '{tool_name}' execution failed: {message}")


class ToolExecutor:
    """
    Unified tool executor that routes tool calls to appropriate handlers.

    Supports:
    - Database-defined tools (ml_model, data_api, external_api)
    - Built-in tools (registered via decorator)
    """

    def __init__(self, session: Session | None = None):
        self.session = session
        self._builtin_tools: dict[str, callable] = {}
        self._tool_cache: dict[str, Tool] = {}

    def register_builtin(self, name: str, handler: callable) -> None:
        """Register a built-in tool handler."""
        self._builtin_tools[name] = handler

    def _get_tool(self, name: str) -> Tool | None:
        """Get tool definition from database."""
        if name in self._tool_cache:
            return self._tool_cache[name]

        if not self.session:
            return None

        tool = self.session.exec(
            select(Tool).where(Tool.name == name, Tool.status == "active")
        ).first()

        if tool:
            self._tool_cache[name] = tool

        return tool

    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> Any:
        """
        Execute a tool by name with the given arguments.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool input arguments
            session_id: Session context
            user_id: User context

        Returns:
            Tool execution result

        Raises:
            ToolExecutionError: If tool not found or execution fails
        """
        start_time = time.time()

        # Check built-in tools first
        if tool_name in self._builtin_tools:
            try:
                result = await self._builtin_tools[tool_name](arguments)
                return result
            except Exception as e:
                raise ToolExecutionError(tool_name, str(e))

        # Look up tool in database
        tool = self._get_tool(tool_name)
        if not tool:
            raise ToolExecutionError(tool_name, "Tool not found")

        # Route to appropriate handler based on tool type
        try:
            if tool.tool_type == "ml_model":
                result = await self._execute_ml_model(tool, arguments)
            elif tool.tool_type == "data_api":
                result = await self._execute_data_api(tool, arguments)
            elif tool.tool_type == "external_api":
                result = await self._execute_external_api(tool, arguments)
            else:
                result = await self._execute_generic(tool, arguments)

            # Update tool statistics
            await self._update_statistics(tool, start_time, success=True)

            return result

        except Exception as e:
            await self._update_statistics(tool, start_time, success=False)
            raise ToolExecutionError(tool_name, str(e))

    async def _execute_ml_model(self, tool: Tool, arguments: dict[str, Any]) -> Any:
        """Execute a machine learning model tool."""
        from app.adapters import ModelFactoryAdapter

        config = tool.service_config
        model_id = config.get("model_id")
        endpoint = config.get("endpoint")

        if not model_id and not endpoint:
            raise ValueError("ML model tool requires model_id or endpoint in service_config")

        adapter = ModelFactoryAdapter()
        result = await adapter.predict(
            model_id=model_id,
            endpoint=endpoint,
            input_data=arguments,
        )

        return result

    async def _execute_data_api(self, tool: Tool, arguments: dict[str, Any]) -> Any:
        """Execute a data warehouse API tool."""
        from app.adapters import DataWarehouseAdapter

        config = tool.service_config
        query_template = config.get("query_template")
        table_name = config.get("table_name")

        adapter = DataWarehouseAdapter()

        if query_template:
            # Use template-based query
            result = await adapter.query_template(query_template, arguments)
        elif table_name:
            # Use table-based query
            result = await adapter.query_table(table_name, arguments)
        else:
            raise ValueError("Data API tool requires query_template or table_name")

        return result

    async def _execute_external_api(self, tool: Tool, arguments: dict[str, Any]) -> Any:
        """Execute an external API tool."""
        from app.adapters import ExternalAPIAdapter

        config = tool.service_config
        url = config.get("url")
        method = config.get("method", "POST")
        headers = config.get("headers", {})

        if not url:
            raise ValueError("External API tool requires url in service_config")

        adapter = ExternalAPIAdapter()
        result = await adapter.call(
            url=url,
            method=method,
            headers=headers,
            data=arguments,
        )

        return result

    async def _execute_generic(self, tool: Tool, arguments: dict[str, Any]) -> Any:
        """Execute a generic tool (fallback)."""
        # For generic tools, we return a placeholder response
        # This should be overridden with specific implementations
        return {
            "tool": tool.name,
            "status": "executed",
            "input": arguments,
            "message": "Generic tool execution - implement specific handler",
        }

    async def _update_statistics(
        self, tool: Tool, start_time: float, success: bool
    ) -> None:
        """Update tool execution statistics."""
        if not self.session:
            return

        latency_ms = (time.time() - start_time) * 1000

        # Update running averages
        old_count = tool.call_count
        new_count = old_count + 1

        # Running average for latency
        if old_count > 0:
            tool.avg_latency_ms = (
                tool.avg_latency_ms * old_count + latency_ms
            ) / new_count
        else:
            tool.avg_latency_ms = latency_ms

        # Running average for success rate
        if old_count > 0:
            tool.success_rate = (
                tool.success_rate * old_count + (1.0 if success else 0.0)
            ) / new_count
        else:
            tool.success_rate = 1.0 if success else 0.0

        tool.call_count = new_count
        tool.updated_at = datetime.utcnow()

        self.session.add(tool)
        self.session.commit()


# Default executor instance (requires session injection per request)
_default_executor: ToolExecutor | None = None


def get_tool_executor(session: Session | None = None) -> ToolExecutor:
    """Get or create a tool executor."""
    return ToolExecutor(session=session)


# Convenience function for use in nfc_graph
async def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
    session_id: str | None = None,
    user_id: str | None = None,
    session: Session | None = None,
) -> Any:
    """
    Execute a tool by name.

    This is a convenience function for the NFC graph.
    """
    executor = get_tool_executor(session)
    return await executor.execute(tool_name, arguments, session_id, user_id)


# ============ Built-in Tool Decorator ============

def builtin_tool(name: str):
    """
    Decorator to register a built-in tool.

    Usage:
        @builtin_tool("calculator")
        async def calculator_tool(args: dict) -> dict:
            ...
    """

    def decorator(func):
        # Register when the module is loaded
        # This is a simple registration - in production you might use a registry
        func._tool_name = name
        return func

    return decorator

"""
Tests for the Tool Executor - Unified tool execution layer

Tests cover:
- ToolExecutionError exception
- ToolExecutor builtin tool registration
- ToolExecutor execution routing
- builtin_tool decorator
- execute_tool convenience function
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.engine.tool_executor import (
    ToolExecutionError,
    ToolExecutor,
    get_tool_executor,
    execute_tool,
    builtin_tool,
)


# ============================================================================
# ToolExecutionError Tests
# ============================================================================

class TestToolExecutionError:
    def test_exception_fields(self):
        """Test ToolExecutionError has correct fields."""
        error = ToolExecutionError("test_tool", "Something failed")
        
        assert error.tool_name == "test_tool"
        assert error.message == "Something failed"
    
    def test_exception_message(self):
        """Test ToolExecutionError string representation."""
        error = ToolExecutionError("my_tool", "Connection timeout")
        
        assert "my_tool" in str(error)
        assert "Connection timeout" in str(error)


# ============================================================================
# ToolExecutor Tests
# ============================================================================

class TestToolExecutor:
    @pytest.fixture
    def executor(self):
        return ToolExecutor(session=None)
    
    def test_register_builtin(self, executor):
        """Test registering a built-in tool handler."""
        async def my_handler(args):
            return {"result": args.get("x", 0) * 2}
        
        executor.register_builtin("double", my_handler)
        
        assert "double" in executor._builtin_tools
        assert executor._builtin_tools["double"] == my_handler
    
    @pytest.mark.anyio
    async def test_execute_builtin_tool(self, executor):
        """Test executing a built-in tool."""
        async def calculator(args):
            return {"sum": args["a"] + args["b"]}
        
        executor.register_builtin("calculator", calculator)
        
        result = await executor.execute("calculator", {"a": 3, "b": 5})
        
        assert result == {"sum": 8}
    
    @pytest.mark.anyio
    async def test_execute_builtin_tool_failure(self, executor):
        """Test built-in tool failure raises ToolExecutionError."""
        async def failing_tool(args):
            raise ValueError("Invalid input")
        
        executor.register_builtin("failing", failing_tool)
        
        with pytest.raises(ToolExecutionError) as exc_info:
            await executor.execute("failing", {})
        
        assert exc_info.value.tool_name == "failing"
        assert "Invalid input" in exc_info.value.message
    
    @pytest.mark.anyio
    async def test_execute_tool_not_found(self, executor):
        """Test executing unknown tool raises error."""
        with pytest.raises(ToolExecutionError) as exc_info:
            await executor.execute("unknown_tool", {})
        
        assert "not found" in exc_info.value.message.lower()
    
    def test_get_tool_no_session(self, executor):
        """Test _get_tool returns None when no session."""
        result = executor._get_tool("any_tool")
        assert result is None
    
    @pytest.mark.anyio
    async def test_execute_caches_builtin_priority(self, executor):
        """Test built-in tools take priority over DB tools."""
        # Register a built-in tool
        async def builtin_version(args):
            return {"source": "builtin"}
        
        executor.register_builtin("test_tool", builtin_version)
        
        # Mock a DB tool with the same name
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        executor._tool_cache["test_tool"] = mock_tool
        
        # Should use built-in
        result = await executor.execute("test_tool", {})
        assert result["source"] == "builtin"


# ============================================================================
# Tool Type Execution Tests (mocked adapters)
# ============================================================================

class TestToolTypeExecution:
    @pytest.fixture
    def executor_with_mock_session(self):
        mock_session = MagicMock()
        return ToolExecutor(session=mock_session)
    
    @pytest.mark.anyio
    async def test_execute_ml_model_tool(self, executor_with_mock_session):
        """Test ML model tool execution."""
        executor = executor_with_mock_session
        
        # Create a mock Tool
        mock_tool = MagicMock()
        mock_tool.name = "credit_score"
        mock_tool.tool_type = "ml_model"
        mock_tool.service_config = {"model_id": "credit-v1"}
        mock_tool.call_count = 0
        mock_tool.avg_latency_ms = 0.0
        mock_tool.success_rate = 1.0
        
        executor._tool_cache["credit_score"] = mock_tool
        
        # Mock the adapter at the correct path (where it's imported)
        with patch("app.adapters.ModelFactoryAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.predict.return_value = {"score": 750}
            MockAdapter.return_value = mock_adapter
            
            result = await executor.execute("credit_score", {"user_id": "123"})
            
            mock_adapter.predict.assert_called_once()
            assert result == {"score": 750}
    
    @pytest.mark.anyio
    async def test_execute_data_api_tool_template(self, executor_with_mock_session):
        """Test data API tool with query template."""
        executor = executor_with_mock_session
        
        mock_tool = MagicMock()
        mock_tool.name = "customer_query"
        mock_tool.tool_type = "data_api"
        mock_tool.service_config = {"query_template": "SELECT * FROM customers WHERE id = $id"}
        mock_tool.call_count = 0
        mock_tool.avg_latency_ms = 0.0
        mock_tool.success_rate = 1.0
        
        executor._tool_cache["customer_query"] = mock_tool
        
        with patch("app.adapters.DataWarehouseAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.query_template.return_value = [{"id": "123", "name": "Acme"}]
            MockAdapter.return_value = mock_adapter
            
            result = await executor.execute("customer_query", {"id": "123"})
            
            mock_adapter.query_template.assert_called_once()
            assert result == [{"id": "123", "name": "Acme"}]
    
    @pytest.mark.anyio
    async def test_execute_external_api_tool(self, executor_with_mock_session):
        """Test external API tool execution."""
        executor = executor_with_mock_session
        
        mock_tool = MagicMock()
        mock_tool.name = "weather_api"
        mock_tool.tool_type = "external_api"
        mock_tool.service_config = {
            "url": "https://api.weather.com/forecast",
            "method": "GET"
        }
        mock_tool.call_count = 0
        mock_tool.avg_latency_ms = 0.0
        mock_tool.success_rate = 1.0
        
        executor._tool_cache["weather_api"] = mock_tool
        
        with patch("app.adapters.ExternalAPIAdapter") as MockAdapter:
            mock_adapter = AsyncMock()
            mock_adapter.call.return_value = {"forecast": "sunny"}
            MockAdapter.return_value = mock_adapter
            
            result = await executor.execute("weather_api", {"city": "Beijing"})
            
            mock_adapter.call.assert_called_once()
            assert result == {"forecast": "sunny"}
    
    @pytest.mark.anyio
    async def test_execute_generic_tool(self, executor_with_mock_session):
        """Test generic tool fallback execution."""
        executor = executor_with_mock_session
        
        mock_tool = MagicMock()
        mock_tool.name = "custom_tool"
        mock_tool.tool_type = "custom_type"
        mock_tool.service_config = {}
        mock_tool.call_count = 0
        mock_tool.avg_latency_ms = 0.0
        mock_tool.success_rate = 1.0
        
        executor._tool_cache["custom_tool"] = mock_tool
        
        result = await executor.execute("custom_tool", {"param": "value"})
        
        assert result["tool"] == "custom_tool"
        assert result["status"] == "executed"


# ============================================================================
# Statistics Update Tests
# ============================================================================

class TestStatisticsUpdate:
    @pytest.mark.anyio
    async def test_update_statistics_success(self):
        """Test statistics update on successful execution."""
        mock_session = MagicMock()
        executor = ToolExecutor(session=mock_session)
        
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.tool_type = "generic"
        mock_tool.service_config = {}
        mock_tool.call_count = 5
        mock_tool.avg_latency_ms = 100.0
        mock_tool.success_rate = 0.8
        
        executor._tool_cache["test_tool"] = mock_tool
        
        await executor.execute("test_tool", {})
        
        # Verify statistics were updated
        assert mock_tool.call_count == 6
        mock_session.add.assert_called()
        mock_session.commit.assert_called()
    
    @pytest.mark.anyio
    async def test_update_statistics_no_session(self):
        """Test stats update is skipped without session."""
        executor = ToolExecutor(session=None)
        
        async def handler(args):
            return {"ok": True}
        
        executor.register_builtin("test", handler)
        
        # Should not raise even without session
        result = await executor.execute("test", {})
        assert result == {"ok": True}


# ============================================================================
# Convenience Function Tests
# ============================================================================

class TestGetToolExecutor:
    def test_creates_new_executor(self):
        """Test get_tool_executor creates new instance."""
        executor1 = get_tool_executor(None)
        executor2 = get_tool_executor(None)
        
        # Each call creates a new instance
        assert executor1 is not executor2
    
    def test_with_session(self):
        """Test get_tool_executor with session."""
        mock_session = MagicMock()
        executor = get_tool_executor(mock_session)
        
        assert executor.session == mock_session


class TestExecuteTool:
    @pytest.mark.anyio
    async def test_execute_tool_function(self):
        """Test execute_tool convenience function."""
        # This will fail because tool is not found, but tests the interface
        with pytest.raises(ToolExecutionError):
            await execute_tool("nonexistent_tool", {"arg": "value"})


# ============================================================================
# Decorator Tests
# ============================================================================

class TestBuiltinToolDecorator:
    def test_decorator_sets_tool_name(self):
        """Test builtin_tool decorator sets _tool_name attribute."""
        @builtin_tool("my_custom_tool")
        async def my_tool(args):
            return args
        
        assert hasattr(my_tool, "_tool_name")
        assert my_tool._tool_name == "my_custom_tool"
    
    @pytest.mark.anyio
    async def test_decorator_preserves_function(self):
        """Test decorator preserves original function."""
        @builtin_tool("adder")
        async def add_numbers(args):
            return args["a"] + args["b"]
        
        # Function should still be callable
        result = await add_numbers({"a": 2, "b": 3})
        assert result == 5

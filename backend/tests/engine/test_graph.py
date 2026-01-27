"""
Tests for the Graph Layer - LangGraph State Graph Definition

Tests cover:
- AgentState TypedDict structure
- should_retry conditional edge logic
- route_by_intent conditional edge logic
- increment_retry node
- error_handler node
- create_agent_graph graph construction
- compile_graph compilation
- run_agent and stream_agent high-level functions
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.engine.graph import (
    AgentState,
    should_retry,
    route_by_intent,
    increment_retry,
    error_handler,
    create_agent_graph,
    compile_graph,
    get_default_graph,
)


# ============================================================================
# Conditional Edge Tests
# ============================================================================

class TestShouldRetry:
    def test_retry_on_validation_failure(self):
        """Test retry when validation fails and retries remaining."""
        state: AgentState = {
            "validation_status": "failed",
            "retry_count": 0,
        }
        
        result = should_retry(state)
        assert result == "retry"
    
    def test_no_retry_when_validation_passed(self):
        """Test no retry when validation passes."""
        state: AgentState = {
            "validation_status": "passed",
            "retry_count": 0,
        }
        
        result = should_retry(state)
        assert result == "end"
    
    def test_no_retry_when_max_retries_exceeded(self):
        """Test no retry when max retries reached."""
        state: AgentState = {
            "validation_status": "failed",
            "retry_count": 2,  # Max retries is 2
        }
        
        result = should_retry(state)
        assert result == "end"
    
    def test_defaults_to_end_for_missing_fields(self):
        """Test defaults handle missing state fields."""
        state: AgentState = {}
        
        result = should_retry(state)
        assert result == "end"


class TestRouteByIntent:
    def test_route_query_intent(self):
        """Test routing for query intent."""
        state: AgentState = {"intent": "query"}
        result = route_by_intent(state)
        assert result == "execute"
    
    def test_route_analysis_intent(self):
        """Test routing for analysis intent."""
        state: AgentState = {"intent": "analysis"}
        result = route_by_intent(state)
        assert result == "execute"
    
    def test_route_prediction_intent(self):
        """Test routing for prediction intent."""
        state: AgentState = {"intent": "prediction"}
        result = route_by_intent(state)
        assert result == "execute"
    
    def test_route_workflow_intent(self):
        """Test routing for workflow intent."""
        state: AgentState = {"intent": "workflow"}
        result = route_by_intent(state)
        assert result == "execute"
    
    def test_route_conversation_intent(self):
        """Test routing for conversation intent."""
        state: AgentState = {"intent": "conversation"}
        result = route_by_intent(state)
        assert result == "execute"
    
    def test_route_unknown_intent(self):
        """Test routing for unknown intent."""
        state: AgentState = {"intent": "unknown"}
        result = route_by_intent(state)
        assert result == "execute"
    
    def test_route_default_for_missing(self):
        """Test default routing when intent is missing."""
        state: AgentState = {}
        result = route_by_intent(state)
        assert result == "execute"


# ============================================================================
# Node Function Tests
# ============================================================================

class TestIncrementRetry:
    @pytest.mark.anyio
    async def test_increment_from_zero(self):
        """Test incrementing retry count from zero."""
        state: AgentState = {"retry_count": 0}
        
        result = await increment_retry(state)
        
        assert result["retry_count"] == 1
    
    @pytest.mark.anyio
    async def test_increment_preserves_state(self):
        """Test increment preserves other state fields."""
        state: AgentState = {
            "input": "test",
            "session_id": "sess-1",
            "retry_count": 1,
        }
        
        result = await increment_retry(state)
        
        assert result["retry_count"] == 2
        assert result["input"] == "test"
        assert result["session_id"] == "sess-1"
    
    @pytest.mark.anyio
    async def test_increment_handles_missing(self):
        """Test increment handles missing retry_count."""
        state: AgentState = {}
        
        result = await increment_retry(state)
        
        assert result["retry_count"] == 1


class TestErrorHandler:
    @pytest.mark.anyio
    async def test_handles_error_message(self):
        """Test error handler captures error message."""
        state: AgentState = {
            "error": "Connection timeout",
        }
        
        result = await error_handler(state)
        
        assert result["validated_output"]["error"] == "Connection timeout"
        assert result["validated_output"]["status"] == "failed"
        assert result["validation_status"] == "failed"
    
    @pytest.mark.anyio
    async def test_handles_missing_error(self):
        """Test error handler with no error message."""
        state: AgentState = {}
        
        result = await error_handler(state)
        
        assert "Unknown error" in result["validated_output"]["error"]
        assert result["validation_status"] == "failed"


# ============================================================================
# Graph Creation Tests
# ============================================================================

class TestCreateAgentGraph:
    def test_creates_graph_with_defaults(self):
        """Test graph creation with default components."""
        graph = create_agent_graph()
        
        assert graph is not None
        # Check nodes are added
        assert "plan" in graph.nodes
        assert "execute" in graph.nodes
        assert "validate" in graph.nodes
        assert "retry" in graph.nodes
        assert "error" in graph.nodes
    
    def test_creates_graph_with_custom_planner(self):
        """Test graph creation with custom planner."""
        mock_planner = MagicMock()
        
        graph = create_agent_graph(planner=mock_planner)
        
        assert graph is not None
        assert "plan" in graph.nodes
    
    def test_creates_graph_with_custom_executor(self):
        """Test graph creation with custom executor."""
        mock_executor = MagicMock()
        
        graph = create_agent_graph(executor=mock_executor)
        
        assert graph is not None
        assert "execute" in graph.nodes
    
    def test_creates_graph_with_custom_validator(self):
        """Test graph creation with custom validator."""
        mock_validator = MagicMock()
        
        graph = create_agent_graph(validator=mock_validator)
        
        assert graph is not None
        assert "validate" in graph.nodes


class TestCompileGraph:
    def test_compile_without_checkpointer(self):
        """Test graph compilation without checkpointer."""
        compiled = compile_graph()
        
        assert compiled is not None
        # Compiled graph should be callable
        assert hasattr(compiled, "ainvoke")
        assert hasattr(compiled, "astream")
    
    def test_compile_with_checkpointer(self):
        """Test graph compilation with checkpointer."""
        mock_checkpointer = MagicMock()
        
        compiled = compile_graph(checkpointer=mock_checkpointer)
        
        assert compiled is not None


class TestGetDefaultGraph:
    def test_returns_compiled_graph(self):
        """Test get_default_graph returns a compiled graph."""
        # Reset global state
        import app.engine.graph as graph_module
        graph_module._default_graph = None
        
        graph = get_default_graph()
        
        assert graph is not None
        assert hasattr(graph, "ainvoke")
    
    def test_caches_graph(self):
        """Test get_default_graph caches the graph."""
        import app.engine.graph as graph_module
        graph_module._default_graph = None
        
        graph1 = get_default_graph()
        graph2 = get_default_graph()
        
        assert graph1 is graph2


# ============================================================================
# AgentState Type Tests
# ============================================================================

class TestAgentState:
    def test_state_creation(self):
        """Test AgentState can be created with all fields."""
        state: AgentState = {
            "input": "Hello",
            "session_id": "sess-123",
            "user_id": "user-456",
            "messages": [],
            "intent": "query",
            "intent_confidence": 0.9,
            "target_agent": "data_query_agent",
            "extracted_params": {"key": "value"},
            "fallback_agents": ["backup_agent"],
            "execution_result": {"data": []},
            "execution_status": "completed",
            "validated_output": {"verified": True},
            "validation_status": "passed",
            "validation_issues": [],
            "error": None,
            "retry_count": 0,
        }
        
        assert state["input"] == "Hello"
        assert state["intent_confidence"] == 0.9
        assert state["retry_count"] == 0
    
    def test_state_partial(self):
        """Test AgentState with partial fields (total=False)."""
        state: AgentState = {
            "input": "Test",
            "session_id": "sess-1",
        }
        
        # Should not require all fields
        assert state["input"] == "Test"
        assert "intent" not in state

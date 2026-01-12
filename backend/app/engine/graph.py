"""
Graph Layer - LangGraph State Graph Definition

Defines the state machine and graph structure for the agent orchestration engine
using LangGraph for stateful, streaming workflows.
"""

from typing import Annotated, Any, Literal

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.engine.executor import Executor, default_executor
from app.engine.planner import Planner, default_planner
from app.engine.validator import Validator, default_validator


class AgentState(TypedDict, total=False):
    """
    State definition for the agent orchestration graph.

    This TypedDict defines all fields that can be passed between nodes.
    Uses LangGraph's annotation system for state updates.
    """

    # Input
    input: str
    session_id: str
    user_id: str | None

    # Messages with LangGraph's message annotation for proper accumulation
    messages: Annotated[list[dict[str, Any]], add_messages]

    # Planner outputs
    intent: str
    intent_confidence: float
    target_agent: str
    extracted_params: dict[str, Any]
    fallback_agents: list[str]

    # Executor outputs
    execution_result: dict[str, Any]
    execution_status: str

    # Validator outputs
    validated_output: dict[str, Any]
    validation_status: str
    validation_issues: list[dict[str, Any]]

    # Error handling
    error: str | None
    retry_count: int


def should_retry(state: AgentState) -> Literal["retry", "end"]:
    """
    Conditional edge: determine if execution should be retried.

    Retries on validation failure up to max retries.
    """
    validation_status = state.get("validation_status", "passed")
    retry_count = state.get("retry_count", 0)
    max_retries = 2

    if validation_status != "passed" and retry_count < max_retries:
        return "retry"
    return "end"


def route_by_intent(state: AgentState) -> str:
    """
    Conditional edge: route to different execution paths based on intent.

    Can be extended to support specialized execution paths.
    """
    intent = state.get("intent", "conversation")

    # For now, all intents go through standard execution
    # This can be extended to route to specialized subgraphs
    intent_to_node: dict[str, str] = {
        "query": "execute",
        "analysis": "execute",
        "prediction": "execute",
        "workflow": "execute",
        "conversation": "execute",
        "unknown": "execute",
    }

    return intent_to_node.get(intent, "execute")


async def increment_retry(state: AgentState) -> AgentState:
    """Helper node to increment retry counter."""
    return {
        **state,
        "retry_count": state.get("retry_count", 0) + 1,
    }


async def error_handler(state: AgentState) -> AgentState:
    """
    Error handling node.

    Captures errors and prepares graceful failure response.
    """
    error = state.get("error")
    return {
        **state,
        "validated_output": {
            "error": error or "Unknown error occurred",
            "status": "failed",
        },
        "validation_status": "failed",
    }


def create_agent_graph(
    planner: Planner | None = None,
    executor: Executor | None = None,
    validator: Validator | None = None,
) -> StateGraph[AgentState, Any, Any, Any]:
    """
    Create the main agent orchestration graph.

    Graph structure:
        START → plan → execute → validate → END
                  ↑                    │
                  └──── retry ←────────┘

    Args:
        planner: Custom planner instance (uses default if None)
        executor: Custom executor instance (uses default if None)
        validator: Custom validator instance (uses default if None)

    Returns:
        Compiled LangGraph StateGraph
    """
    planner = planner or default_planner
    executor = executor or default_executor
    validator = validator or default_validator

    # Create the graph with AgentState
    graph = StateGraph(AgentState)

    # Add nodes
    # Suppress Mypy errors due to strict TypeVar matching in LangGraph
    graph.add_node("plan", planner)
    graph.add_node("execute", executor)
    graph.add_node("validate", validator)
    graph.add_node("retry", increment_retry)
    graph.add_node("error", error_handler)

    # Add edges
    graph.add_edge(START, "plan")

    # Conditional routing after planning
    graph.add_conditional_edges(
        "plan",
        route_by_intent,
        {
            "execute": "execute",
            "error": "error",
        },
    )

    graph.add_edge("execute", "validate")

    # Conditional retry logic after validation
    graph.add_conditional_edges(
        "validate",
        should_retry,
        {
            "retry": "retry",
            "end": END,
        },
    )

    graph.add_edge("retry", "plan")
    graph.add_edge("error", END)

    return graph


def compile_graph(
    planner: Planner | None = None,
    executor: Executor | None = None,
    validator: Validator | None = None,
    checkpointer: Any | None = None,
) -> Any:
    """
    Compile the graph for execution.

    Args:
        planner: Custom planner instance
        executor: Custom executor instance
        validator: Custom validator instance
        checkpointer: LangGraph checkpointer for state persistence

    Returns:
        Compiled graph ready for invocation
    """
    graph = create_agent_graph(planner, executor, validator)

    compile_kwargs: dict[str, Any] = {}
    if checkpointer:
        compile_kwargs["checkpointer"] = checkpointer

    return graph.compile(**compile_kwargs)


async def run_agent(
    input_text: str,
    session_id: str,
    user_id: str | None = None,
    **kwargs: Any,
) -> Any:
    """
    High-level function to run the agent graph.

    Args:
        input_text: User input message
        session_id: Session identifier
        user_id: Optional user identifier
        **kwargs: Additional configuration

    Returns:
        Final state after graph execution
    """
    graph = compile_graph()

    initial_state: AgentState = {
        "input": input_text,
        "session_id": session_id,
        "user_id": user_id,
        "messages": [],
        "retry_count": 0,
        **kwargs,  # type: ignore[typeddict-item]
    }

    # Run the graph
    result = await graph.ainvoke(initial_state)

    return result


async def stream_agent(
    input_text: str,
    session_id: str,
    user_id: str | None = None,
    **kwargs: Any,
) -> Any:
    """
    Stream agent execution with real-time updates.

    Yields state updates as the graph progresses through nodes.

    Args:
        input_text: User input message
        session_id: Session identifier
        user_id: Optional user identifier
        **kwargs: Additional configuration

    Yields:
        State snapshots as graph executes
    """
    graph = compile_graph()

    initial_state: AgentState = {
        "input": input_text,
        "session_id": session_id,
        "user_id": user_id,
        "messages": [],
        "retry_count": 0,
        **kwargs,  # type: ignore[typeddict-item]
    }

    # Stream graph execution
    async for event in graph.astream(initial_state):
        yield event


# Pre-compiled default graph for efficiency
_default_graph = None


def get_default_graph() -> Any:
    """Get or create the default compiled graph."""
    global _default_graph
    if _default_graph is None:
        _default_graph = compile_graph()
    return _default_graph

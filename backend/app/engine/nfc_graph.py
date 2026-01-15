"""
Native Function Calling Graph - ReAct Loop Implementation

This module implements a Native Function Calling (NFC) style agent graph
that uses the LLM's built-in tool_use capability in a ReAct loop pattern.

Flow:
    START → think → [tool_call] → execute_tool → think → ... → respond → END
"""

from typing import Annotated, Any, AsyncIterator, Literal
import uuid

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from sqlmodel import Session

from app.llm import LLMGateway
from app.llm.base import (
    LLMConfig,
    Message,
    MessageRole,
    ToolCall,
    ToolDefinition,
)


class NFCAgentState(TypedDict, total=False):
    """
    State definition for Native Function Calling agent.

    This state tracks the conversation and tool execution in a ReAct loop.
    """

    # Session info
    session_id: str
    user_id: str | None

    # Conversation history (LangGraph message accumulation)
    messages: Annotated[list[dict[str, Any]], add_messages]

    # Current input
    input: str

    # LLM configuration
    model: str
    provider_id: str | None
    temperature: float

    # Available tools for this session
    available_tools: list[ToolDefinition]

    # Current tool calls pending execution
    pending_tool_calls: list[ToolCall]

    # Tool execution results
    tool_results: list[dict[str, Any]]

    # Final response (set when done)
    final_response: str | None
    
    # Chain of thought content (DeepSeek R1 etc)
    reasoning_content: str | None

    # Iteration tracking
    iteration: int
    max_iterations: int

    # Status
    status: str  # "thinking", "tool_calling", "responding", "done", "error"
    error: str | None


# ============ Node Functions ============

async def think_node(state: NFCAgentState, gateway: LLMGateway) -> dict[str, Any]:
    """
    Think node: Call LLM with current context and available tools.

    The LLM decides whether to:
    1. Call one or more tools
    2. Provide a final response
    """
    messages = state.get("messages", [])
    tools = state.get("available_tools", [])
    model = state.get("model", "deepseek-chat")
    temperature = state.get("temperature", 0.7)

    # Build messages for LLM
    llm_messages = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        llm_messages.append(Message(
            role=MessageRole(role) if role in ["system", "user", "assistant", "tool"] else MessageRole.USER,
            content=content,
            tool_calls=msg.get("tool_calls"),
            tool_call_id=msg.get("tool_call_id"),
            name=msg.get("name"),
        ))

    # Add current input if this is the first iteration
    if state.get("iteration", 0) == 0:
        llm_messages.append(Message(role=MessageRole.USER, content=state.get("input", "")))

    # Call LLM with tools
    config = LLMConfig(
        model=model,
        temperature=temperature,
        tools=tools if tools else None,
        tool_choice="auto" if tools else None,
    )

    response = await gateway.chat(
        messages=llm_messages,
        config=config,
        provider_id=state.get("provider_id"),
    )

    # Check if LLM wants to call tools
    if response.has_tool_calls:
        return {
            "pending_tool_calls": response.tool_calls,
            "messages": [response.to_message().to_dict()],
            "status": "tool_calling",
            "iteration": state.get("iteration", 0) + 1,
            "reasoning_content": response.reasoning_content,
        }
    else:
        # LLM provided final response
        return {
            "final_response": response.content,
            "messages": [response.to_message().to_dict()],
            "status": "done",
            "pending_tool_calls": [],
            "reasoning_content": response.reasoning_content,
        }


async def execute_tools_node(state: NFCAgentState) -> dict[str, Any]:
    """
    Execute pending tool calls and collect results.
    """
    from app.engine.tool_executor import execute_tool

    pending_calls = state.get("pending_tool_calls", [])
    results = []
    result_messages = []

    for tool_call in pending_calls:
        try:
            # Execute the tool
            result = await execute_tool(
                tool_name=tool_call.name,
                arguments=tool_call.arguments,
                session_id=state.get("session_id", ""),
                user_id=state.get("user_id"),
            )

            results.append({
                "tool_call_id": tool_call.id,
                "tool_name": tool_call.name,
                "result": result,
                "success": True,
            })

            # Add tool result message for conversation
            result_messages.append({
                "role": "tool",
                "content": str(result) if not isinstance(result, str) else result,
                "tool_call_id": tool_call.id,
                "name": tool_call.name,
            })

        except Exception as e:
            results.append({
                "tool_call_id": tool_call.id,
                "tool_name": tool_call.name,
                "error": str(e),
                "success": False,
            })

            result_messages.append({
                "role": "tool",
                "content": f"Error: {str(e)}",
                "tool_call_id": tool_call.id,
                "name": tool_call.name,
            })

    return {
        "tool_results": results,
        "messages": result_messages,
        "pending_tool_calls": [],
        "status": "thinking",
    }


async def respond_node(state: NFCAgentState) -> dict[str, Any]:
    """
    Final response node - prepare the response for output.
    """
    return {
        "status": "done",
    }


async def error_node(state: NFCAgentState) -> dict[str, Any]:
    """
    Error handling node.
    """
    return {
        "status": "error",
        "final_response": f"An error occurred: {state.get('error', 'Unknown error')}",
    }


# ============ Conditional Edges ============

def should_continue(state: NFCAgentState) -> Literal["execute_tools", "respond", "think"]:
    """
    Determine next step after thinking.
    """
    status = state.get("status", "thinking")
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 10)

    if status == "tool_calling" and iteration < max_iterations:
        return "execute_tools"
    elif status == "done":
        return "respond"
    else:
        # Max iterations reached or error - respond
        return "respond"


def after_tool_execution(state: NFCAgentState) -> Literal["think", "respond"]:
    """
    Determine next step after tool execution.
    """
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 10)

    if iteration < max_iterations:
        return "think"
    else:
        return "respond"


# ============ Graph Builder ============

def create_nfc_graph(gateway: LLMGateway) -> StateGraph:
    """
    Create the Native Function Calling agent graph.

    Graph structure:
        START → think → [tool_calling?] → execute_tools → think → ... → respond → END
                  ↓ [done]
               respond → END
    """
    graph = StateGraph(NFCAgentState)

    # Create node functions with gateway bound
    async def think(state: NFCAgentState) -> dict[str, Any]:
        return await think_node(state, gateway)

    # Add nodes
    graph.add_node("think", think)
    graph.add_node("execute_tools", execute_tools_node)
    graph.add_node("respond", respond_node)
    graph.add_node("error", error_node)

    # Add edges
    graph.add_edge(START, "think")

    # Conditional routing after thinking
    graph.add_conditional_edges(
        "think",
        should_continue,
        {
            "execute_tools": "execute_tools",
            "respond": "respond",
            "think": "think",  # For continuation
        },
    )

    # After tool execution, go back to thinking
    graph.add_conditional_edges(
        "execute_tools",
        after_tool_execution,
        {
            "think": "think",
            "respond": "respond",
        },
    )

    graph.add_edge("respond", END)
    graph.add_edge("error", END)

    return graph


def compile_nfc_graph(
    gateway: LLMGateway,
    checkpointer: Any | None = None,
) -> Any:
    """
    Compile the NFC graph for execution.
    """
    graph = create_nfc_graph(gateway)

    compile_kwargs: dict[str, Any] = {}
    if checkpointer:
        compile_kwargs["checkpointer"] = checkpointer

    return graph.compile(**compile_kwargs)


# ============ High-Level API ============

async def run_nfc_agent(
    input_text: str,
    session_id: str,
    user_id: str | None = None,
    model: str = "deepseek-chat",
    provider_id: str | None = None,
    tools: list[ToolDefinition] | None = None,
    session: Session | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Run the NFC agent with the given input.

    Args:
        input_text: User input message
        session_id: Session identifier
        user_id: Optional user identifier
        model: LLM model to use
        tools: Available tool definitions
        session: Database session for gateway
        **kwargs: Additional configuration

    Returns:
        Final state with response
    """
    gateway = LLMGateway(session=session, user_id=uuid.UUID(user_id) if user_id else None)
    graph = compile_nfc_graph(gateway)

    initial_state: NFCAgentState = {
        "input": input_text,
        "session_id": session_id,
        "user_id": user_id,
        "model": model,
        "provider_id": provider_id,
        "temperature": kwargs.get("temperature", 0.7),
        "available_tools": tools or [],
        "messages": kwargs.get("messages", []),
        "pending_tool_calls": [],
        "tool_results": [],
        "final_response": None,
        "reasoning_content": None,
        "iteration": 0,
        "max_iterations": kwargs.get("max_iterations", 10),
        "status": "thinking",
        "error": None,
    }

    result = await graph.ainvoke(initial_state)
    return result


async def stream_nfc_agent(
    input_text: str,
    session_id: str,
    user_id: str | None = None,
    model: str = "deepseek-chat",
    provider_id: str | None = None,
    tools: list[ToolDefinition] | None = None,
    session: Session | None = None,
    **kwargs: Any,
) -> AsyncIterator[dict[str, Any]]:
    """
    Stream the NFC agent execution with real-time updates.

    Yields state updates as the graph progresses through nodes.
    """
    gateway = LLMGateway(session=session, user_id=uuid.UUID(user_id) if user_id else None)
    graph = compile_nfc_graph(gateway)

    initial_state: NFCAgentState = {
        "input": input_text,
        "session_id": session_id,
        "user_id": user_id,
        "model": model,
        "provider_id": provider_id,
        "temperature": kwargs.get("temperature", 0.7),
        "available_tools": tools or [],
        "messages": kwargs.get("messages", []),
        "pending_tool_calls": [],
        "tool_results": [],
        "final_response": None,
        "reasoning_content": None,
        "iteration": 0,
        "max_iterations": kwargs.get("max_iterations", 10),
        "status": "thinking",
        "error": None,
    }

    async for event in graph.astream(initial_state):
        yield event

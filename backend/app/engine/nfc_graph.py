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
from app.engine.planner import LLMPlanner



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
    status: str  # "thinking", "tool_calling", "validating", "responding", "done", "error"
    error: str | None
    
    # Planning data (Perception/Intent/Steps)
    planning_data: dict[str, Any] | None
    
    # Validation data (from validator layer)
    validation_status: str | None  # "passed", "failed", "warning"
    validation_issues: list[dict[str, Any]]

# ============ Node Functions ============

async def plan_node(state: NFCAgentState, gateway: LLMGateway) -> dict[str, Any]:
    """
    Planning node: Analyze intent and create a plan before execution.
    """
    # Only plan on the first iteration
    if state.get("iteration", 0) > 0:
        return {}
        
    planner = LLMPlanner(gateway)
    message = state.get("input", "")
    context = state.get("messages", [])
    model = state.get("model", "deepseek-chat")
    
    # Execute planning
    # We might want to pass available tools to the planner implicitly or explicitly if needed
    # For now, general planning is fine.
    try:
        decision = await planner.plan(message, context, model=model)
        
        return {
            "planning_data": {
                "intent": decision.intent.type.value,
                "confidence": decision.intent.confidence,
                "reasoning": decision.intent.metadata.get("reasoning", ""),
                "steps": decision.intent.metadata.get("plan_steps", []),
                "entities": decision.params.to_dict()
            },
            "status": "thinking"
        }
    except Exception as e:
        print(f"Planning failed: {e}")
        return {"planning_data": {"error": str(e)}}


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
        "status": "validating",
    }


async def validate_node(state: NFCAgentState) -> dict[str, Any]:
    """
    Validate tool execution results.
    
    Checks for:
    - Result structure and completeness
    - Sensitive data exposure
    - Compliance with data policies
    
    Sanitizes sensitive data in results.
    """
    from app.engine.validator import default_validator
    
    tool_results = state.get("tool_results", [])
    validation_issues: list[dict[str, Any]] = []
    overall_status = "passed"
    
    for result in tool_results:
        if not result.get("success"):
            continue
            
        # Validate and sanitize each successful result
        result_data = result.get("result", {})
        if isinstance(result_data, dict):
            validated = await default_validator.validate({
                "execution_result": result_data
            })
            
            # Collect issues
            issues = validated.get("validation_issues", [])
            if issues:
                validation_issues.extend(issues)
                
            # Update overall status
            if validated.get("validation_status") == "failed":
                overall_status = "failed"
            elif validated.get("validation_status") == "warning" and overall_status == "passed":
                overall_status = "warning"
                
            # Use sanitized output
            result["result"] = validated.get("validated_output", result_data)
    
    return {
        "tool_results": tool_results,
        "validation_status": overall_status,
        "validation_issues": validation_issues,
        "status": "thinking",  # Continue to thinking after validation
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


def after_tool_execution(state: NFCAgentState) -> Literal["validate"]:
    """
    Determine next step after tool execution.
    Always go to validation first.
    """
    return "validate"


def after_validation(state: NFCAgentState) -> Literal["think", "respond"]:
    """
    Determine next step after validation.
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

    async def plan(state: NFCAgentState) -> dict[str, Any]:
        return await plan_node(state, gateway)

    # Add nodes
    graph.add_node("plan", plan)
    graph.add_node("think", think)
    graph.add_node("execute_tools", execute_tools_node)
    graph.add_node("validate", validate_node)
    graph.add_node("respond", respond_node)
    graph.add_node("error", error_node)

    # Add edges
    # START -> plan -> think
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "think")


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

    # After tool execution, go to validation
    graph.add_conditional_edges(
        "execute_tools",
        after_tool_execution,
        {
            "validate": "validate",
        },
    )
    
    # After validation, go back to thinking or respond
    graph.add_conditional_edges(
        "validate",
        after_validation,
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
    thread_id: str | None = None,
    use_checkpointer: bool = False,
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
        thread_id: Thread ID for checkpointer (enables state persistence)
        use_checkpointer: Whether to enable state persistence
        **kwargs: Additional configuration

    Returns:
        Final state with response
    """
    gateway = LLMGateway(session=session, user_id=uuid.UUID(user_id) if user_id else None)
    
    # Get checkpointer if enabled
    checkpointer = None
    if use_checkpointer:
        from app.engine.checkpointer import get_checkpointer
        checkpointer = await get_checkpointer()
    
    graph = compile_nfc_graph(gateway, checkpointer=checkpointer)

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
        "planning_data": None,
    }

    # Build config with thread_id for checkpointer
    config = {}
    if thread_id or use_checkpointer:
        config["configurable"] = {"thread_id": thread_id or session_id}

    result = await graph.ainvoke(initial_state, config=config if config else None)
    return result


async def stream_nfc_agent(
    input_text: str,
    session_id: str,
    user_id: str | None = None,
    model: str = "deepseek-chat",
    provider_id: str | None = None,
    tools: list[ToolDefinition] | None = None,
    session: Session | None = None,
    thread_id: str | None = None,
    use_checkpointer: bool = False,
    **kwargs: Any,
) -> AsyncIterator[dict[str, Any]]:
    """
    Stream the NFC agent execution with real-time updates.

    Yields state updates as the graph progresses through nodes.
    
    Args:
        input_text: User input message
        session_id: Session identifier
        user_id: Optional user identifier
        model: LLM model to use
        tools: Available tool definitions
        session: Database session for gateway
        thread_id: Thread ID for checkpointer (enables state persistence)
        use_checkpointer: Whether to enable state persistence
        **kwargs: Additional configuration
    """
    gateway = LLMGateway(session=session, user_id=uuid.UUID(user_id) if user_id else None)
    
    # Get checkpointer if enabled
    checkpointer = None
    if use_checkpointer:
        from app.engine.checkpointer import get_checkpointer
        checkpointer = await get_checkpointer()
    
    graph = compile_nfc_graph(gateway, checkpointer=checkpointer)

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
        "planning_data": None,
    }

    # Build config with thread_id for checkpointer
    config = {}
    if thread_id or use_checkpointer:
        config["configurable"] = {"thread_id": thread_id or session_id}

    async for event in graph.astream(initial_state, config=config if config else None):
        yield event

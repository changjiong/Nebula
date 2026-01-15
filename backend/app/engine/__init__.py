"""
Engine Module

LangGraph-based agent orchestration engine with:
- Planner: intent understanding, agent routing
- Executor: DAG scheduling, service calls
- Validator: result verification
- Memory: context management
- Graph: LangGraph state machine definition
- NFC Graph: Native Function Calling ReAct loop (NEW)
- Tool Executor: Unified tool execution layer (NEW)
"""

from app.engine.executor import (
    DAGScheduler,
    Executor,
    ParallelExecutor,
    SSEStreamHandler,
    default_executor,
)
from app.engine.graph import (
    AgentState,
    compile_graph,
    create_agent_graph,
    get_default_graph,
    run_agent,
    stream_agent,
)
from app.engine.memory import (
    ConversationMemory,
    MemoryStore,
    SessionState,
    async_memory_store,
    memory_store,
)
from app.engine.nfc_graph import (
    NFCAgentState,
    compile_nfc_graph,
    create_nfc_graph,
    run_nfc_agent,
    stream_nfc_agent,
)
from app.engine.planner import (
    AgentRouter,
    Intent,
    IntentType,
    Planner,
    default_planner,
)
from app.engine.tool_executor import (
    ToolExecutionError,
    ToolExecutor,
    builtin_tool,
    execute_tool,
    get_tool_executor,
)
from app.engine.validator import (
    ComplianceChecker,
    OutputSanitizer,
    ResultValidator,
    ValidationResult,
    Validator,
    default_validator,
)

__all__ = [
    # Memory
    "ConversationMemory",
    "SessionState",
    "MemoryStore",
    "memory_store",
    "async_memory_store",
    # Planner
    "IntentType",
    "Intent",
    "AgentRouter",
    "Planner",
    "default_planner",
    # Executor
    "DAGScheduler",
    "ParallelExecutor",
    "Executor",
    "SSEStreamHandler",
    "default_executor",
    # Validator
    "ResultValidator",
    "ComplianceChecker",
    "OutputSanitizer",
    "ValidationResult",
    "Validator",
    "default_validator",
    # Graph (traditional)
    "AgentState",
    "create_agent_graph",
    "compile_graph",
    "run_agent",
    "stream_agent",
    "get_default_graph",
    # NFC Graph (Native Function Calling)
    "NFCAgentState",
    "create_nfc_graph",
    "compile_nfc_graph",
    "run_nfc_agent",
    "stream_nfc_agent",
    # Tool Executor
    "ToolExecutor",
    "ToolExecutionError",
    "execute_tool",
    "get_tool_executor",
    "builtin_tool",
]


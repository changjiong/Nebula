# Agent Portal Engine

This module implements the core LangGraph-based agent orchestration engine.

## Layers

- `planner.py` - Planning layer: intent understanding, agent routing
- `executor.py` - Execution layer: DAG scheduling, service calls
- `validator.py` - Validation layer: result verification
- `memory.py` - Memory layer: context management
- `graph.py` - LangGraph graph definition

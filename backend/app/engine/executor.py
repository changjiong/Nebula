"""
Executor Layer - DAG Scheduling and Parallel Execution

Provides DAG-based task scheduling, parallel execution, and SSE streaming
for the LangGraph agent orchestration engine.
"""

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    """Status of a task in the execution DAG."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """Represents a single task in the execution DAG."""

    id: str
    name: str
    handler: Callable[..., Any]
    dependencies: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_ready(self, completed_tasks: set[str]) -> bool:
        """Check if all dependencies are completed."""
        return all(dep in completed_tasks for dep in self.dependencies)


@dataclass
class SSEEvent:
    """Server-Sent Event for streaming output."""

    event: str  # Event type: "message", "progress", "error", "complete"
    data: dict[str, Any]
    id: str | None = None
    retry: int | None = None

    def to_sse_format(self) -> str:
        """Format as SSE wire protocol."""
        import json

        lines = []
        if self.id:
            lines.append(f"id: {self.id}")
        if self.retry:
            lines.append(f"retry: {self.retry}")
        lines.append(f"event: {self.event}")
        lines.append(f"data: {json.dumps(self.data, ensure_ascii=False)}")
        lines.append("")  # Trailing newline
        return "\n".join(lines)


class SSEStreamHandler:
    """
    Handles Server-Sent Events streaming for real-time output.

    Provides async iteration interface for streaming responses.
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue[SSEEvent | None] = asyncio.Queue()
        self._closed = False

    async def emit(
        self,
        event: str,
        data: dict[str, Any],
        event_id: str | None = None,
    ) -> None:
        """Emit an SSE event to the stream."""
        if self._closed:
            return
        sse_event = SSEEvent(event=event, data=data, id=event_id)
        await self._queue.put(sse_event)

    async def emit_progress(
        self,
        task_id: str,
        progress: float,
        message: str | None = None,
    ) -> None:
        """Emit a progress update event."""
        await self.emit(
            "progress",
            {"task_id": task_id, "progress": progress, "message": message},
        )

    async def emit_message(self, content: str, role: str = "assistant") -> None:
        """Emit a message content event."""
        await self.emit("message", {"content": content, "role": role})

    async def emit_error(self, error: str, task_id: str | None = None) -> None:
        """Emit an error event."""
        await self.emit("error", {"error": error, "task_id": task_id})

    async def emit_complete(self, result: dict[str, Any] | None = None) -> None:
        """Emit completion event and close the stream."""
        await self.emit("complete", {"result": result or {}})
        await self.close()

    async def close(self) -> None:
        """Close the stream."""
        self._closed = True
        await self._queue.put(None)  # Sentinel value

    async def __aiter__(self) -> AsyncIterator[str]:
        """Iterate over SSE events as formatted strings."""
        while True:
            event = await self._queue.get()
            if event is None:
                break
            yield event.to_sse_format()


class DAGScheduler:
    """
    Schedules task execution based on dependency graph.

    Supports parallel execution of independent tasks.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def add_task(
        self,
        task_id: str,
        name: str,
        handler: Callable[..., Any],
        dependencies: list[str] | None = None,
        **metadata: Any,
    ) -> Task:
        """Add a task to the DAG."""
        task = Task(
            id=task_id,
            name=name,
            handler=handler,
            dependencies=dependencies or [],
            metadata=metadata,
        )
        self._tasks[task_id] = task
        return task

    def get_ready_tasks(self, completed: set[str]) -> list[Task]:
        """Get all tasks that are ready to execute."""
        return [
            task
            for task in self._tasks.values()
            if task.status == TaskStatus.PENDING and task.is_ready(completed)
        ]

    def get_execution_order(self) -> list[list[str]]:
        """
        Get tasks grouped by execution level (parallelizable groups).

        Returns a list of task ID lists, where tasks in the same list
        can be executed in parallel.
        """
        completed: set[str] = set()
        levels: list[list[str]] = []

        while len(completed) < len(self._tasks):
            ready = self.get_ready_tasks(completed)
            if not ready:
                # Cycle detection
                remaining = [
                    t.id
                    for t in self._tasks.values()
                    if t.id not in completed
                ]
                raise ValueError(f"Dependency cycle detected: {remaining}")

            level = [t.id for t in ready]
            levels.append(level)
            completed.update(level)

        return levels

    def clear(self) -> None:
        """Clear all tasks."""
        self._tasks.clear()


class TaskExecutor(ABC):
    """Abstract base class for task execution."""

    @abstractmethod
    async def execute(
        self,
        task: Task,
        context: dict[str, Any],
    ) -> Any:
        """Execute a single task."""
        ...


class DefaultTaskExecutor(TaskExecutor):
    """Default task executor that runs the task handler."""

    async def execute(
        self,
        task: Task,
        context: dict[str, Any],
    ) -> Any:
        """Execute task handler with context."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        try:
            if asyncio.iscoroutinefunction(task.handler):
                result = await task.handler(context)
            else:
                result = task.handler(context)

            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            return result

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            raise


class ParallelExecutor:
    """
    Executes tasks in parallel based on DAG dependencies.

    Provides streaming progress updates via SSE.
    """

    def __init__(
        self,
        scheduler: DAGScheduler | None = None,
        task_executor: TaskExecutor | None = None,
        max_concurrency: int = 10,
    ) -> None:
        self.scheduler = scheduler or DAGScheduler()
        self.task_executor = task_executor or DefaultTaskExecutor()
        self.max_concurrency = max_concurrency
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def execute_all(
        self,
        context: dict[str, Any],
        stream_handler: SSEStreamHandler | None = None,
    ) -> dict[str, Any]:
        """
        Execute all tasks in the DAG with parallelism.

        Returns aggregated results from all tasks.
        """
        execution_order = self.scheduler.get_execution_order()
        results: dict[str, Any] = {}

        for level_idx, level in enumerate(execution_order):
            # Report progress
            if stream_handler:
                await stream_handler.emit_progress(
                    task_id="dag",
                    progress=(level_idx + 1) / len(execution_order),
                    message=f"Executing level {level_idx + 1}/{len(execution_order)}",
                )

            # Execute all tasks in this level in parallel
            level_tasks = [self.scheduler._tasks[tid] for tid in level]
            level_results = await self._execute_level(
                level_tasks, context, stream_handler
            )
            results.update(level_results)

            # Update context with results for next level
            context = {**context, "results": results}

        return results

    async def _execute_level(
        self,
        tasks: list[Task],
        context: dict[str, Any],
        stream_handler: SSEStreamHandler | None = None,
    ) -> dict[str, Any]:
        """Execute a level of tasks in parallel."""

        async def run_task(task: Task) -> tuple[str, Any]:
            async with self._semaphore:
                if stream_handler:
                    await stream_handler.emit_progress(
                        task_id=task.id,
                        progress=0.0,
                        message=f"Starting task: {task.name}",
                    )

                try:
                    result = await self.task_executor.execute(task, context)
                    if stream_handler:
                        await stream_handler.emit_progress(
                            task_id=task.id,
                            progress=1.0,
                            message=f"Completed task: {task.name}",
                        )
                    return (task.id, result)
                except Exception as e:
                    if stream_handler:
                        await stream_handler.emit_error(str(e), task.id)
                    return (task.id, {"error": str(e)})

        results = await asyncio.gather(*[run_task(t) for t in tasks])
        return dict(results)


class Executor:
    """
    Main executor component for the LangGraph engine.

    Acts as a LangGraph node for the execution phase.
    """

    def __init__(
        self,
        parallel_executor: ParallelExecutor | None = None,
    ) -> None:
        self.parallel_executor = parallel_executor or ParallelExecutor()

    async def execute(
        self,
        state: dict[str, Any],
        stream_handler: SSEStreamHandler | None = None,
    ) -> dict[str, Any]:
        """
        Execute the planned tasks.

        Reads target_agent and extracted_params from state,
        dispatches to appropriate handler, returns results.
        """
        target_agent = state.get("target_agent", "chat_agent")
        params = state.get("extracted_params", {})

        # For simple cases, execute directly
        # For complex workflows, use DAG scheduling
        if stream_handler:
            await stream_handler.emit_message(
                f"Executing with agent: {target_agent}"
            )

        # Placeholder for actual agent execution
        result = {
            "agent": target_agent,
            "params": params,
            "output": f"Executed {target_agent} successfully",
            "timestamp": datetime.now().isoformat(),
        }

        if stream_handler:
            await stream_handler.emit_progress(
                task_id="main",
                progress=1.0,
                message="Execution completed",
            )

        return {
            **state,
            "execution_result": result,
            "execution_status": "completed",
        }

    async def __call__(
        self, state: dict[str, Any]
    ) -> dict[str, Any]:
        """LangGraph node interface for execution."""
        return await self.execute(state)


# Default executor instance
default_executor = Executor()

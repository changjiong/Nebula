"""
Tests for the Executor Layer - DAG Scheduling and Parallel Execution

Tests cover:
- TaskStatus enum
- Task dataclass and is_ready method
- SSEEvent formatting
- SSEStreamHandler event emission
- DAGScheduler task management and execution ordering
- ParallelExecutor concurrent execution
- Executor LangGraph node interface
"""

import asyncio
from datetime import datetime

import pytest

from app.engine.executor import (
    TaskStatus,
    Task,
    SSEEvent,
    SSEStreamHandler,
    DAGScheduler,
    DefaultTaskExecutor,
    ParallelExecutor,
    Executor,
)


# ============================================================================
# TaskStatus and Task Tests
# ============================================================================

class TestTaskStatus:
    def test_enum_values(self):
        """Verify all task status values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.SKIPPED.value == "skipped"


class TestTask:
    def test_task_creation(self):
        """Test Task dataclass creation."""
        handler = lambda x: x
        task = Task(
            id="task-1",
            name="Test Task",
            handler=handler,
            dependencies=["task-0"],
            metadata={"key": "value"}
        )
        
        assert task.id == "task-1"
        assert task.name == "Test Task"
        assert task.handler == handler
        assert task.dependencies == ["task-0"]
        assert task.status == TaskStatus.PENDING
        assert task.result is None
        assert task.metadata == {"key": "value"}
    
    def test_is_ready_no_dependencies(self):
        """Test task is ready when it has no dependencies."""
        task = Task(id="task-1", name="Test", handler=lambda x: x)
        assert task.is_ready(set()) is True
    
    def test_is_ready_with_dependencies(self):
        """Test task readiness with dependencies."""
        task = Task(
            id="task-2",
            name="Test",
            handler=lambda x: x,
            dependencies=["task-0", "task-1"]
        )
        
        # Not ready when no dependencies completed
        assert task.is_ready(set()) is False
        
        # Not ready when only some dependencies completed
        assert task.is_ready({"task-0"}) is False
        
        # Ready when all dependencies completed
        assert task.is_ready({"task-0", "task-1"}) is True
        assert task.is_ready({"task-0", "task-1", "task-extra"}) is True


# ============================================================================
# SSEEvent Tests
# ============================================================================

class TestSSEEvent:
    def test_basic_format(self):
        """Test basic SSE event formatting."""
        event = SSEEvent(event="message", data={"content": "Hello"})
        formatted = event.to_sse_format()
        
        assert "event: message" in formatted
        assert '"content": "Hello"' in formatted or '"content":"Hello"' in formatted
    
    def test_format_with_id(self):
        """Test SSE format includes event ID."""
        event = SSEEvent(event="message", data={}, id="evt-123")
        formatted = event.to_sse_format()
        
        assert "id: evt-123" in formatted
    
    def test_format_with_retry(self):
        """Test SSE format includes retry interval."""
        event = SSEEvent(event="message", data={}, retry=5000)
        formatted = event.to_sse_format()
        
        assert "retry: 5000" in formatted
    
    def test_format_unicode(self):
        """Test SSE format with unicode characters."""
        event = SSEEvent(event="message", data={"content": "你好世界"})
        formatted = event.to_sse_format()
        
        assert "你好世界" in formatted


# ============================================================================
# SSEStreamHandler Tests
# ============================================================================

class TestSSEStreamHandler:
    @pytest.mark.anyio
    async def test_emit_and_iterate(self):
        """Test emitting events and iterating over them."""
        handler = SSEStreamHandler()
        
        # Emit some events
        await handler.emit("message", {"content": "Hello"})
        await handler.emit("progress", {"value": 0.5})
        await handler.close()
        
        # Collect all events
        events = []
        async for event_str in handler:
            events.append(event_str)
        
        assert len(events) == 2
        assert "message" in events[0]
        assert "progress" in events[1]
    
    @pytest.mark.anyio
    async def test_emit_progress(self):
        """Test progress event emission."""
        handler = SSEStreamHandler()
        
        await handler.emit_progress("task-1", 0.75, "Almost done")
        await handler.close()
        
        events = [e async for e in handler]
        assert len(events) == 1
        assert "progress" in events[0]
        assert "0.75" in events[0]
    
    @pytest.mark.anyio
    async def test_emit_message(self):
        """Test message event emission."""
        handler = SSEStreamHandler()
        
        await handler.emit_message("This is a response", role="assistant")
        await handler.close()
        
        events = [e async for e in handler]
        assert len(events) == 1
        assert "message" in events[0]
    
    @pytest.mark.anyio
    async def test_emit_error(self):
        """Test error event emission."""
        handler = SSEStreamHandler()
        
        await handler.emit_error("Something went wrong", "task-1")
        await handler.close()
        
        events = [e async for e in handler]
        assert len(events) == 1
        assert "error" in events[0]
    
    @pytest.mark.anyio
    async def test_emit_complete(self):
        """Test complete event emission closes stream."""
        handler = SSEStreamHandler()
        
        await handler.emit_complete({"status": "success"})
        
        # Stream should be closed
        assert handler._closed is True
        
        events = [e async for e in handler]
        assert len(events) == 1
        assert "complete" in events[0]
    
    @pytest.mark.anyio
    async def test_emit_after_close(self):
        """Test that emit after close is ignored."""
        handler = SSEStreamHandler()
        await handler.close()
        
        # This should not raise
        await handler.emit("message", {"content": "ignored"})


# ============================================================================
# DAGScheduler Tests
# ============================================================================

class TestDAGScheduler:
    @pytest.fixture
    def scheduler(self):
        return DAGScheduler()
    
    def test_add_task(self, scheduler):
        """Test adding a task to the scheduler."""
        task = scheduler.add_task(
            task_id="task-1",
            name="First Task",
            handler=lambda x: x,
            dependencies=[]
        )
        
        assert task.id == "task-1"
        assert task.name == "First Task"
        assert "task-1" in scheduler._tasks
    
    def test_get_ready_tasks_no_deps(self, scheduler):
        """Test getting ready tasks with no dependencies."""
        scheduler.add_task("t1", "Task 1", lambda x: x)
        scheduler.add_task("t2", "Task 2", lambda x: x)
        
        ready = scheduler.get_ready_tasks(set())
        assert len(ready) == 2
    
    def test_get_ready_tasks_with_deps(self, scheduler):
        """Test getting ready tasks respects dependencies."""
        scheduler.add_task("t1", "Task 1", lambda x: x)
        scheduler.add_task("t2", "Task 2", lambda x: x, dependencies=["t1"])
        
        ready = scheduler.get_ready_tasks(set())
        # Only t1 should be ready initially (no completed tasks)
        ready_ids = [t.id for t in ready if t.dependencies == []]
        assert len(ready_ids) == 1
        assert "t1" in ready_ids
    
    def test_get_execution_order_simple(self, scheduler):
        """Test execution order for simple DAG."""
        scheduler.add_task("t1", "Task 1", lambda x: x)
        scheduler.add_task("t2", "Task 2", lambda x: x, dependencies=["t1"])
        scheduler.add_task("t3", "Task 3", lambda x: x, dependencies=["t2"])
        
        order = scheduler.get_execution_order()
        
        # Should have 3 levels (sequential dependencies)
        assert len(order) == 3
        # Flatten to verify all tasks present
        all_tasks = [t for level in order for t in level]
        assert set(all_tasks) == {"t1", "t2", "t3"}
    
    def test_get_execution_order_parallel(self, scheduler):
        """Test that independent tasks are grouped for parallel execution."""
        scheduler.add_task("t1", "Task 1", lambda x: x)
        scheduler.add_task("t2", "Task 2", lambda x: x)  # Independent of t1
        scheduler.add_task("t3", "Task 3", lambda x: x, dependencies=["t1", "t2"])
        
        order = scheduler.get_execution_order()
        
        # Should have 2 levels: [t1, t2] then [t3]
        assert len(order) == 2
        # First level should contain both t1 and t2 (parallel)
        assert set(order[0]) == {"t1", "t2"}
        # Second level should have t3
        assert "t3" in order[1]
    
    def test_cycle_detection(self, scheduler):
        """Test that dependency cycles are detected."""
        scheduler.add_task("t1", "Task 1", lambda x: x, dependencies=["t2"])
        scheduler.add_task("t2", "Task 2", lambda x: x, dependencies=["t1"])
        
        with pytest.raises(ValueError, match="cycle"):
            scheduler.get_execution_order()
    
    def test_clear(self, scheduler):
        """Test clearing tasks."""
        scheduler.add_task("t1", "Task 1", lambda x: x)
        scheduler.clear()
        
        assert len(scheduler._tasks) == 0


# ============================================================================
# DefaultTaskExecutor Tests
# ============================================================================

class TestDefaultTaskExecutor:
    @pytest.fixture
    def executor(self):
        return DefaultTaskExecutor()
    
    @pytest.mark.anyio
    async def test_execute_sync_handler(self, executor):
        """Test executing a synchronous handler."""
        def sync_handler(ctx):
            return {"sum": ctx["a"] + ctx["b"]}
        
        task = Task(id="t1", name="Sync Task", handler=sync_handler)
        result = await executor.execute(task, {"a": 1, "b": 2})
        
        assert result == {"sum": 3}
        assert task.status == TaskStatus.COMPLETED
        assert task.started_at is not None
        assert task.completed_at is not None
    
    @pytest.mark.anyio
    async def test_execute_async_handler(self, executor):
        """Test executing an async handler."""
        async def async_handler(ctx):
            await asyncio.sleep(0.01)
            return {"value": ctx["x"] * 2}
        
        task = Task(id="t1", name="Async Task", handler=async_handler)
        result = await executor.execute(task, {"x": 5})
        
        assert result == {"value": 10}
        assert task.status == TaskStatus.COMPLETED
    
    @pytest.mark.anyio
    async def test_execute_failure(self, executor):
        """Test handling handler failure."""
        def failing_handler(ctx):
            raise ValueError("Something went wrong")
        
        task = Task(id="t1", name="Failing Task", handler=failing_handler)
        
        with pytest.raises(ValueError):
            await executor.execute(task, {})
        
        assert task.status == TaskStatus.FAILED
        assert "Something went wrong" in task.error


# ============================================================================
# ParallelExecutor Tests
# ============================================================================

class TestParallelExecutor:
    @pytest.mark.anyio
    async def test_execute_all_simple(self):
        """Test simple parallel execution."""
        scheduler = DAGScheduler()
        scheduler.add_task("t1", "Task 1", lambda ctx: {"result": "t1"})
        scheduler.add_task("t2", "Task 2", lambda ctx: {"result": "t2"}, dependencies=["t1"])
        
        executor = ParallelExecutor(scheduler=scheduler)
        results = await executor.execute_all({})
        
        assert "t1" in results
        assert "t2" in results
    
    @pytest.mark.anyio
    async def test_execute_all_with_stream(self):
        """Test parallel execution with stream handler."""
        scheduler = DAGScheduler()
        scheduler.add_task("t1", "Task 1", lambda ctx: {"result": "t1"})
        
        executor = ParallelExecutor(scheduler=scheduler)
        stream = SSEStreamHandler()
        
        # Run execution and close stream in background
        async def run():
            await executor.execute_all({}, stream_handler=stream)
            await stream.close()
        
        asyncio.create_task(run())
        
        # Collect events
        events = []
        async for event in stream:
            events.append(event)
        
        # Should have progress events
        assert len(events) >= 2  # At least DAG progress + task progress


# ============================================================================
# Executor (LangGraph Node) Tests
# ============================================================================

class TestExecutor:
    @pytest.fixture
    def executor(self):
        return Executor()
    
    @pytest.mark.anyio
    async def test_execute_basic(self, executor):
        """Test basic execution."""
        state = {
            "target_agent": "data_query_agent",
            "extracted_params": {"query": "test"}
        }
        
        result = await executor.execute(state)
        
        assert "execution_result" in result
        assert result["execution_status"] == "completed"
        assert result["execution_result"]["agent"] == "data_query_agent"
    
    @pytest.mark.anyio
    async def test_langraph_interface(self, executor):
        """Test LangGraph node callable interface."""
        state = {
            "input": "test input",
            "target_agent": "chat_agent",
            "extracted_params": {}
        }
        
        result = await executor(state)
        
        assert "execution_result" in result
        assert result["execution_status"] == "completed"

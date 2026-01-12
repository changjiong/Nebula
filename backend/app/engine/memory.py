"""
Memory Layer - Session Context Management

Provides session state management, conversation history, and context windowing
for the LangGraph agent orchestration engine.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Message:
    """Represents a single message in conversation history."""

    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationMemory:
    """
    Manages conversation history for a session.

    Provides sliding window functionality to maintain context
    within token limits while preserving important messages.
    """

    messages: list[Message] = field(default_factory=list)
    max_messages: int = 50
    system_prompt: str | None = None

    def add_message(self, role: str, content: str, **metadata: Any) -> None:
        """Add a message to conversation history."""
        message = Message(role=role, content=content, metadata=metadata)
        self.messages.append(message)
        self._trim_if_needed()

    def _trim_if_needed(self) -> None:
        """Trim oldest messages if exceeding max limit."""
        if len(self.messages) > self.max_messages:
            # Keep system messages and recent messages
            system_msgs = [m for m in self.messages if m.role == "system"]
            other_msgs = [m for m in self.messages if m.role != "system"]
            keep_count = self.max_messages - len(system_msgs)
            self.messages = system_msgs + other_msgs[-keep_count:]

    def get_context_window(self, window_size: int | None = None) -> list[Message]:
        """Get recent messages within the context window."""
        size = window_size or self.max_messages
        return self.messages[-size:]

    def to_langchain_messages(self) -> list[dict[str, str]]:
        """Convert to LangChain message format."""
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def clear(self) -> None:
        """Clear all messages except system prompt."""
        self.messages = [m for m in self.messages if m.role == "system"]


@dataclass
class SessionState:
    """
    Represents the current state of an agent session.

    Tracks execution progress, intermediate results, and agent-specific data.
    """

    session_id: str
    user_id: str | None = None
    current_intent: str | None = None
    extracted_params: dict[str, Any] = field(default_factory=dict)
    execution_results: list[dict[str, Any]] = field(default_factory=list)
    validation_status: str = "pending"  # pending, passed, failed
    error_message: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def update(self, **kwargs: Any) -> None:
        """Update session state fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()


class MemoryStore:
    """
    Central memory store for managing multiple sessions.

    Provides session lifecycle management and shared context access.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}
        self._conversations: dict[str, ConversationMemory] = {}

    def create_session(
        self,
        session_id: str,
        user_id: str | None = None,
        system_prompt: str | None = None,
    ) -> SessionState:
        """Create a new session with associated conversation memory."""
        session = SessionState(session_id=session_id, user_id=user_id)
        self._sessions[session_id] = session

        conversation = ConversationMemory(system_prompt=system_prompt)
        if system_prompt:
            conversation.add_message("system", system_prompt)
        self._conversations[session_id] = conversation

        return session

    def get_session(self, session_id: str) -> SessionState | None:
        """Retrieve an existing session."""
        return self._sessions.get(session_id)

    def get_conversation(self, session_id: str) -> ConversationMemory | None:
        """Retrieve conversation memory for a session."""
        return self._conversations.get(session_id)

    def update_session(self, session_id: str, **kwargs: Any) -> SessionState | None:
        """Update session state."""
        session = self._sessions.get(session_id)
        if session:
            session.update(**kwargs)
        return session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its conversation memory."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            self._conversations.pop(session_id, None)
            return True
        return False

    def list_sessions(self, user_id: str | None = None) -> list[SessionState]:
        """List all sessions, optionally filtered by user."""
        sessions = list(self._sessions.values())
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        return sessions


class AsyncMemoryStore(MemoryStore):
    """
    Async-compatible memory store for use with async LangGraph nodes.

    Extends MemoryStore with async iteration support for streaming contexts.
    """

    async def stream_conversation(
        self, session_id: str
    ) -> AsyncIterator[Message]:
        """Stream messages from conversation history."""
        conversation = self.get_conversation(session_id)
        if conversation:
            for message in conversation.messages:
                yield message

    async def async_update_session(
        self, session_id: str, **kwargs: Any
    ) -> SessionState | None:
        """Async wrapper for session updates."""
        return self.update_session(session_id, **kwargs)


# Global memory store instance (can be replaced with Redis-backed implementation)
memory_store = MemoryStore()
async_memory_store = AsyncMemoryStore()

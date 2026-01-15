from contextvars import ContextVar
from asyncio import Queue
from typing import NamedTuple

class StreamContext(NamedTuple):
    queue: Queue
    model: str | None = None

# Global context variable to hold stream queue
stream_context_var: ContextVar[StreamContext | None] = ContextVar("stream_context", default=None)
